"""
Test script for Metadata Vision Agent System

Tests the agent with sample inputs to verify functionality.
"""

import os
from dotenv import load_dotenv
from backend import extract_metadata

# Load environment variables
load_dotenv()

def test_url_extraction():
    """Test metadata extraction from URL."""
    print("=" * 60)
    print("TEST 1: URL Extraction")
    print("=" * 60)
    
    # Sample product URL
    test_url = "https://images.pexels.com/photos/90946/pexels-photo-90946.jpeg?cs=srgb&dl=pexels-madebymath-90946.jpg&fm=jpg"
    
    try:
        result = extract_metadata(
            input_data=test_url,
            input_type="url"
        )
        
        print("\n✓ URL extraction completed")
        print(f"\nExtracted Metadata:")
        for key, value in result.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"\n✗ URL extraction failed: {e}")


def test_text_extraction():
    """Test metadata extraction from text."""
    print("\n" + "=" * 60)
    print("TEST 2: Text Extraction")
    print("=" * 60)
    
    # Sample product description
    test_text = """
    Nike Air Max 90 Running Shoes
    Brand: Nike
    Color: White/Black/Red
    Material: Leather and mesh upper
    Size: Available in US 8-13
    Description: Classic running shoe with visible Air cushioning unit.
    Features breathable mesh and durable leather construction.
    """
    
    try:
        result = extract_metadata(
            input_data=test_text,
            input_type="text"
        )
        
        print("\n✓ Text extraction completed")
        print(f"\nExtracted Metadata:")
        for key, value in result.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"\n✗ Text extraction failed: {e}")


def test_image_extraction():
    """Test metadata extraction from image."""
    print("\n" + "=" * 60)
    print("TEST 3: Image Extraction")
    print("=" * 60)
    
    # Real product image URL (sneaker photo from Unsplash)
    sample_image_url = "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800"
    
    print(f"\nUsing sample image: Nike sneaker")
    print(f"Image URL: {sample_image_url}")
    
    try:
        result = extract_metadata(
            input_data=sample_image_url,
            input_type="image"
        )
        
        print("\n✓ Image extraction completed")
        print(f"\nExtracted Metadata:")
        for key, value in result.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"\n✗ Image extraction failed: {e}")
        import traceback
        traceback.print_exc()


def test_structured_output():
    """Test structured output format."""
    print("\n" + "=" * 60)
    print("TEST 4: Structured Output Validation")
    print("=" * 60)
    
    test_text = "Apple MacBook Pro 16-inch, Space Gray, Aluminum chassis"
    
    try:
        result = extract_metadata(
            input_data=test_text,
            input_type="text"
        )
        
        print("\n✓ Extraction completed")
        print(f"\nFull result structure:")
        print(f"Type: {type(result)}")
        print(f"Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        # Check if result is a dictionary
        assert isinstance(result, dict), "Result should be a dictionary"
        
        # Check for expected fields
        expected_fields = ["title", "brand", "category", "color", "material", "dimensions", "description"]
        
        print(f"\nChecking for expected fields:")
        for field in expected_fields:
            present = field in result
            value = result.get(field, 'N/A')
            symbol = "✓" if present else "○"
            print(f"  {symbol} {field}: {value}")
        
        # Check that at least title is present or we have raw_response
        if "title" in result or "raw_response" in result:
            print("\n✓ Structured output validation passed")
        else:
            print("\n⚠ Warning: Neither 'title' nor 'raw_response' found in result")
            print(f"Result contains: {result}")
        
    except AssertionError as e:
        print(f"\n✗ Validation failed: {e}")
    except Exception as e:
        print(f"\n✗ Structured output test failed: {e}")
        import traceback
        traceback.print_exc()



def main():
    """Run tests - ONE AT A TIME to avoid rate limits."""
    print("\n" + "=" * 60)
    print("METADATA VISION AGENT - TEST SUITE")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("\n⚠ WARNING: GOOGLE_API_KEY not found in environment")
        print("Please set your Google API key in .env file")
        print("\nTests will fail without API key.\n")
        return
    
    print("\n⚠️  RATE LIMIT WARNING:")
    print("Google Gemini free tier: 15 requests/minute")
    print("Running ONE test at a time to avoid rate limits.")
    print("=" * 60)
    
    # Run ONLY ONE test at a time
    # Uncomment the test you want to run:
    
    # test_text_extraction()        # ✅ Works - extracts from text description
    # test_structured_output()      # ✅ Quick validation test (recommended)
    # test_url_extraction()         # Requires valid product URL
    test_image_extraction()       # ✅ Test vision extraction with sample image
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("\nTo run other tests:")
    print("1. Wait 1-2 minutes (rate limit reset)")
    print("2. Comment out current test, uncomment another")
    print("3. Run: py test_agent.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
