"""
Metadata Vision Agent System - Core Backend Module

A LangChain v1 + LangGraph agentic system for autonomous product metadata extraction
from multimodal inputs (images, PDFs, URLs).
"""

import os
import re
from dataclasses import dataclass
from typing import Optional, Literal, Any, Dict
from dotenv import load_dotenv

from langchain.agents import create_agent, AgentState
from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime
from langchain.agents.structured_output import ToolStrategy
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import HumanMessage, AIMessage

# HTML parsing
from bs4 import BeautifulSoup
import requests

# Load environment variables
load_dotenv()


# ============================================================================
# STRUCTURED OUTPUT SCHEMA
# ============================================================================

@dataclass
class ProductMetadata:
    """Structured product metadata output schema."""
    title: str
    brand: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    dimensions: Optional[str] = None
    description: Optional[str] = None
    confidence_score: float = 0.0


# ============================================================================
# CUSTOM STATE SCHEMA
# ============================================================================

class MetadataExtractionState(AgentState):
    """Custom state for metadata extraction agent."""
    # Input data
    input_type: Literal["image", "url", "text"]
    input_data: Any
    
    # Extraction status
    html_content: Optional[str] = None
    vision_observations: Optional[str] = None
    validation_errors: Optional[list] = None
    
    # Final metadata
    extracted_metadata: Optional[Dict] = None


# ============================================================================
# TOOLS
# ============================================================================

@tool
def html_scraper_tool(url: str) -> str:
    """
    Extract visible text and metadata from product webpages.
    
    Args:
        url: Product page URL to scrape
        
    Returns:
        Extracted text and metadata as string
    """
    try:
        # Fetch the page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract title
        title = soup.title.string if soup.title else ""
        
        # Extract meta tags
        meta_description = ""
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag and meta_tag.get("content"):
            meta_description = meta_tag["content"]
        
        # Extract visible text
        text = soup.get_text(separator=" ", strip=True)
        
        # Limit text length
        text = text[:5000] if len(text) > 5000 else text
        
        result = f"""
URL: {url}
Title: {title}
Meta Description: {meta_description}

Page Content:
{text}
"""
        return result.strip()
        
    except Exception as e:
        return f"Error scraping URL: {str(e)}"


@tool
def vision_extractor_tool(
    image_description: str,
    runtime: ToolRuntime[None, MetadataExtractionState]
) -> str:
    """
    Use vision LLM to extract product metadata from images.
    
    Args:
        image_description: Description of what to look for in the image
        runtime: Tool runtime with access to state
        
    Returns:
        Vision observations as string
    """
    try:
        # Get image data from state
        state = runtime.state
        
        if state.get("input_type") != "image":
            return "Error: Vision tool requires image input"
        
        image_data = state.get("input_data")
        
        # Initialize vision model
        vision_model = init_chat_model(
            "google_genai:gemini-2.5-flash-lite",
            temperature=0.3,
            max_tokens=2048
        )
        
        # Create message with image
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": f"""Analyze this product image and extract the following information:
{image_description}

Focus on:
- Product name/title
- Brand (if visible)
- Colors
- Materials (if identifiable)
- Approximate dimensions or size indicators
- Any text visible on the product or packaging
- Product category

Be specific and accurate. If something is not visible, say "Not visible in image"."""
                },
                {
                    "type": "image_url",
                    "image_url": image_data
                }
            ]
        )
        
        # Get vision model response
        response = vision_model.invoke([message])
        
        return response.content
        
    except Exception as e:
        return f"Error in vision extraction: {str(e)}"


@tool
def schema_validator_tool(metadata_json: str) -> str:
    """
    Validate extracted metadata against the ProductMetadata schema.
    
    Args:
        metadata_json: JSON string of extracted metadata
        
    Returns:
        Validation result and any errors
    """
    import json
    
    try:
        # Parse JSON
        data = json.loads(metadata_json)
        
        # Required fields
        required = ["title"]
        errors = []
        
        # Check required fields
        for field in required:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Check title length
        if "title" in data and len(data["title"]) < 3:
            errors.append("Title too short (minimum 3 characters)")
        
        # Check for hallucination indicators
        hallucination_phrases = [
            "not visible", "cannot determine", "unclear",
            "not specified", "unknown", "n/a"
        ]
        
        warnings = []
        for field, value in data.items():
            if isinstance(value, str):
                value_lower = value.lower()
                for phrase in hallucination_phrases:
                    if phrase in value_lower:
                        warnings.append(f"Field '{field}' may contain uncertain data: {value}")
        
        # Compile results
        if errors:
            return f"Validation FAILED:\n" + "\n".join(f"- {e}" for e in errors)
        elif warnings:
            return f"Validation PASSED with warnings:\n" + "\n".join(f"- {w}" for w in warnings)
        else:
            return "Validation PASSED: All fields valid"
            
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {str(e)}"
    except Exception as e:
        return f"Validation error: {str(e)}"


@tool
def cleaner_tool(field_name: str, field_value: str) -> str:
    """
    Normalize and clean malformed product data (sizes, colors, materials).
    
    Args:
        field_name: Name of the field to clean (e.g., 'color', 'material', 'dimensions')
        field_value: Raw value to clean
        
    Returns:
        Cleaned value
    """
    if not field_value:
        return field_value
    
    cleaned = field_value.strip()
    
    # Color normalization
    if field_name.lower() == "color":
        color_mappings = {
            r'\bblk\b': 'black',
            r'\bwht\b': 'white',
            r'\bred\b': 'red',
            r'\bblu\b': 'blue',
            r'\bgrn\b': 'green',
        }
        for pattern, replacement in color_mappings.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    
    # Material normalization
    elif field_name.lower() == "material":
        material_mappings = {
            r'\bcotton\b': 'Cotton',
            r'\bpolyester\b': 'Polyester',
            r'\bwool\b': 'Wool',
            r'\bsilk\b': 'Silk',
            r'\bleather\b': 'Leather',
        }
        for pattern, replacement in material_mappings.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    
    # Dimensions normalization
    elif field_name.lower() == "dimensions":
        # Standardize units
        cleaned = re.sub(r'\binches\b', 'in', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\bcentimeters\b', 'cm', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\bmillimeters\b', 'mm', cleaned, flags=re.IGNORECASE)
    
    # Remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned


# ============================================================================
# AGENT SETUP
# ============================================================================

class MetadataExtractionAgent:
    """Main agent class for metadata extraction."""
    
    def __init__(
        self,
        model_name: str = "google_genai:gemini-2.5-flash",
        temperature: float = 0.3,
        max_tokens: int = 20000
    ):
        """
        Initialize the metadata extraction agent.
        
        Args:
            model_name: LLM model to use (format: "provider:model")
            temperature: Model temperature
            max_tokens: Maximum tokens to generate
        """
        # Initialize model
        self.model = init_chat_model(
            model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Tools
        self.tools = [
            html_scraper_tool,
            vision_extractor_tool,
            schema_validator_tool,
            cleaner_tool
        ]
        
        # System prompt with built-in validation instructions
        self.system_prompt = """You are an expert product metadata extraction agent with built-in quality validation.

Your job is to extract accurate, structured metadata from product inputs (images, URLs, or text).

**Tools available:**
- html_scraper_tool: Extract text and metadata from product URLs
- vision_extractor_tool: Analyze product images to extract visual information
- schema_validator_tool: Validate extracted metadata against schema
- cleaner_tool: Normalize and clean malformed data fields

**Process:**
1. Analyze the input type (image, URL, or text)
2. Use appropriate tools to extract information
3. Gather all relevant product attributes
4. Clean and normalize data using cleaner_tool
5. **CRITICAL: Always use schema_validator_tool before finalizing**
6. If validation fails, correct the issues and validate again
7. Calculate confidence_score based on extraction completeness
8. Return structured output in the ProductMetadata schema format

**Quality Rules:**
- Always extract at minimum the product title (REQUIRED)
- Generate a 'description' that reads like a professional e-commerce product page. It MUST explicitly detail the visual attributes (e.g., 'Red upper with white sole' instead of just 'Red'), and naturally weave in the product title, brand, and category. The tone should be engaging and descriptive.
- Use vision_extractor_tool for image inputs
- Use html_scraper_tool for URL inputs
- Never fabricate information - if unsure, leave field as null or use appropriate qualifier
- Use cleaner_tool to normalize colors, materials, and dimensions
- Self-validate for hallucinations, missing fields, and inconsistencies
- Only return final answer after schema_validator_tool confirms validation PASSED

**CRITICAL - Confidence Score Calculation:**
You MUST calculate confidence_score (0.0 to 1.0) based on this formula:
- Start with 0.0
- Add 0.20 for each field successfully extracted: brand, category, color, material, dimensions
- Title is REQUIRED, so it doesn't add to confidence
- Maximum score is 1.0 (all 5 optional fields extracted)

Examples:
- Only title extracted: confidence_score = 0.0
- Title + brand + color: confidence_score = 0.4
- Title + brand + category + color + material: confidence_score = 0.8
- All fields extracted: confidence_score = 1.0

You MUST include the confidence_score field in your final output. This is NON-NEGOTIABLE."""
        
        # Create agent
        # Pass schema directly - LangChain auto-selects ProviderStrategy for Gemini
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=self.system_prompt,
            state_schema=MetadataExtractionState,
            response_format=ProductMetadata,  # Auto-selects ProviderStrategy for Gemini
            checkpointer=InMemorySaver()
        )
    
    def extract(
        self,
        input_data: Any,
        input_type: Literal["image", "url", "text"],
        thread_id: str = "default"
    ) -> Dict:
        """
        Extract metadata from input.
        
        Args:
            input_data: Input data (base64 image, URL string, or text)
            input_type: Type of input
            thread_id: Unique thread identifier for conversation memory
            
        Returns:
            Extracted metadata as dictionary
        """
        # Prepare initial message
        if input_type == "image":
            user_message = "Extract product metadata from the provided image."
        elif input_type == "url":
            user_message = f"Extract product metadata from this URL: {input_data}"
        else:
            user_message = f"Extract product metadata from this text: {input_data}"
        
        # Configure agent
        config = {"configurable": {"thread_id": thread_id}}
        
        # Invoke agent
        response = self.agent.invoke(
            {
                "messages": [{"role": "user", "content": user_message}],
                "input_type": input_type,
                "input_data": input_data
            },
            config=config
        )
        
        # Try to extract structured response (multiple methods)
        result = None

        # Method 1: Check for structured_response key
        if "structured_response" in response:
            metadata = response["structured_response"]
            if hasattr(metadata, "__dataclass_fields__"):
                from dataclasses import asdict
                result = asdict(metadata)
            else:
                result = metadata

        # Method 2: Check for response_format output
        elif "output" in response:
            output = response["output"]
            if isinstance(output, dict):
                result = output
            elif hasattr(output, "__dataclass_fields__"):
                from dataclasses import asdict
                result = asdict(output)

        # Method 3: Try to parse JSON from the last message
        if not result:
            messages = response.get("messages", [])
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, "content"):
                    content = last_message.content

                    # Try to extract JSON from content
                    import json
                    import re

                    # Look for JSON in the response
                    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
                    if json_match:
                        try:
                            result = json.loads(json_match.group(0))
                        except json.JSONDecodeError:
                            pass

                    # If no JSON found, return raw response
                    if not result:
                        result = {"raw_response": content}

        if not result:
            return {"error": "Failed to extract metadata"}

        # FALLBACK: Calculate confidence_score if missing or 0.0
        if "confidence_score" not in result or result.get("confidence_score", 0.0) == 0.0:
            # Calculate based on how many optional fields are present
            optional_fields = ["brand", "category", "color", "material", "dimensions"]
            filled_fields = sum(1 for field in optional_fields if result.get(field))
            result["confidence_score"] = round(filled_fields * 0.20, 2)

        return result


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def extract_metadata(
    input_data: Any,
    input_type: Literal["image", "url", "text"] = "image",
    model_name: str = "google_genai:gemini-2.5-flash",
    temperature: float = 0.2,
    max_tokens: int = 1024
) -> Dict:
    """
    Convenience function to extract product metadata.
    
    Args:
        input_data: Input data (base64 image, URL, or text)
        input_type: Type of input ("image", "url", or "text")
        model_name: LLM model to use (format: "provider:model")
        temperature: Model temperature (0.0-1.0)
        max_tokens: Maximum tokens to generate
        
    Returns:
        Extracted metadata dictionary
        
    Example:
        ```python
        from backend import extract_metadata
        
        # Extract from image
        metadata = extract_metadata(
            input_data="data:image/png;base64,iVBORw0KG...",
            input_type="image"
        )
        ```
    """
    agent = MetadataExtractionAgent(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return agent.extract(
        input_data=input_data,
        input_type=input_type
    )
