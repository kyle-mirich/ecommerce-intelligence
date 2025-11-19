# Metadata Vision Agent System

A LangChain v1 + LangGraph agentic system for autonomous product metadata extraction from multimodal inputs.

## Overview

The Metadata Vision Agent System (MVAS) uses a fully agentic pipeline to extract, validate, and structure product metadata from:
- Product images
- Product URLs
- Text descriptions
- PDF documents

## Features

- **Autonomous Extraction**: ReAct-style agent with specialized tools
- **Multimodal Support**: Handle images, URLs, PDFs, and text
- **Validation Middleware**: Critic agent checks for hallucinations and missing data
- **Structured Output**: Enforced JSON schema for consistent results
- **Clean Python API**: Direct import, no web framework required

## Architecture

### Core Components

1. **Agent**: LangChain `create_agent` with Google Gemini vision model
2. **Tools**:
   - `html_scraper_tool`: Extract text from product URLs
   - `vision_extractor_tool`: Analyze product images
   - `schema_validator_tool`: Validate metadata completeness
   - `cleaner_tool`: Normalize data (colors, materials, dimensions)
3. **Middleware**: Critic validation for quality assurance
4. **State**: Custom state schema tracking extraction progress

### Output Schema

```python
{
    "title": str,           # Required
    "brand": str | None,
    "category": str | None,
    "color": str | None,
    "material": str | None,
    "dimensions": str | None,
    "description": str | None
}
```

## Installation

### Prerequisites

- Python 3.10+
- Google API key ([Get one here](https://ai.google.dev/gemini-api/docs/api-key))

### Setup

1. **Clone and navigate to project:**
   ```bash
   cd vision-ai-metadata-app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
GOOGLE_API_KEY=your_google_api_key_here
```

## How It Works

1. **Input Processing**: Agent receives multimodal input (image/URL/text)
2. **Tool Selection**: ReAct loop decides which tools to use
3. **Data Extraction**: Tools extract raw product information
4. **Normalization**: Cleaner tool standardizes data format
5. **Validation**: Schema validator checks completeness
6. **Critic Review**: Middleware checks for hallucinations
7. **Structured Output**: Returns validated JSON

## License

MIT

## Contributing

This is a demonstration project. For production use, consider:
- Adding persistent checkpointer (database-backed)
- Implementing retry logic for API calls
- Adding rate limiting
- Expanding test coverage
- Adding support for more file formats
