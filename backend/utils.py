"""
Utility functions for file processing and conversion.
"""

import base64
import io
from typing import Optional
from PIL import Image


def load_image_as_base64(image_data: bytes, mime_type: str = "image/png") -> str:
    """
    Convert image bytes to base64 encoded data URI.
    
    Args:
        image_data: Raw image bytes
        mime_type: MIME type of the image (default: image/png)
        
    Returns:
        Base64 encoded data URI string
    """
    encoded = base64.b64encode(image_data).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def process_uploaded_image(uploaded_file) -> dict:
    """
    Process an uploaded image file for agent consumption.
    
    Args:
        uploaded_file: File-like object from Streamlit uploader
        
    Returns:
        Dict with image data and metadata
    """
    # Read image bytes
    image_bytes = uploaded_file.read()
    
    # Get MIME type
    mime_type = uploaded_file.type if hasattr(uploaded_file, 'type') else 'image/png'
    
    # Convert to base64
    base64_image = load_image_as_base64(image_bytes, mime_type)
    
    return {
        "type": "image",
        "data": base64_image,
        "filename": uploaded_file.name if hasattr(uploaded_file, 'name') else "image.png",
        "mime_type": mime_type
    }


def extract_pdf_page_as_image(pdf_bytes: bytes, page_num: int = 0) -> Optional[str]:
    """
    Extract a page from PDF as an image (base64).
    
    Args:
        pdf_bytes: Raw PDF bytes
        page_num: Page number to extract (0-indexed)
        
    Returns:
        Base64 encoded image data URI or None if extraction fails
    """
    try:
        import fitz  # PyMuPDF
        
        # Open PDF from bytes
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Get the specified page
        if page_num >= len(pdf_document):
            page_num = 0
            
        page = pdf_document[page_num]
        
        # Render page to image (pixmap)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
        
        # Convert to PNG bytes
        img_bytes = pix.tobytes("png")
        
        # Convert to base64
        return load_image_as_base64(img_bytes, "image/png")
        
    except ImportError:
        print("Warning: PyMuPDF (fitz) not installed. PDF extraction disabled.")
        return None
    except Exception as e:
        print(f"Error extracting PDF page: {e}")
        return None


def validate_image_format(image_bytes: bytes) -> bool:
    """
    Validate if bytes represent a valid image.
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        True if valid image, False otherwise
    """
    try:
        Image.open(io.BytesIO(image_bytes))
        return True
    except Exception:
        return False
