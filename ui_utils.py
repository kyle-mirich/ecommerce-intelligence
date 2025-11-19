import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def render_header():
    """Renders the standard header for all pages."""
    # Display banner if it exists
    if os.path.exists("app_banner.png"):
        st.image("app_banner.png", width="stretch")
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding-top: 2rem;
        }
        .metric-card {
            background-color: #ffffff;
            border: 1px solid #e6e9ef;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renders the configuration sidebar and returns settings."""
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        # API Key Status
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            st.success("✅ API Key Loaded")
        else:
            st.error("❌ API Key Missing")
            st.info("Please set GOOGLE_API_KEY in .env file")
            
        st.divider()
        
        # Model Settings
        st.subheader("Model Settings")
        model_name = st.selectbox(
            "Model",
            ["google_genai:gemini-2.5-flash-lite", "google_genai:gemini-1.5-flash"],
            index=0
        )
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
        
        st.divider()
        st.markdown("### About")
        st.markdown("""
        **Metadata Vision Agent** extracts structured product data from:
        - 🖼️ Images
        - 🔗 URLs
        - 📝 Text
        
        Powered by **LangChain v1** & **Google Gemini**.
        """)
        
        return api_key, model_name, temperature

def display_results(metadata):
    """Display extracted metadata in a clean format."""
    if not metadata:
        return

    # Check for error
    if "error" in metadata:
        st.error(f"Extraction Failed: {metadata['error']}")
        return

    # Create a product page layout
    
    # Breadcrumbs / Header Info
    st.markdown(f"**{metadata.get('brand', 'Brand')}** • {metadata.get('category', 'Category')}")
    
    # Title
    st.title(metadata.get("title", "Unknown Product"))
    
    # Confidence Badge
    confidence = metadata.get('confidence_score', 0.0) or 0.0
    color = "green" if confidence > 0.8 else "orange" if confidence > 0.5 else "red"
    st.markdown(f":{color}[Confidence Score: {confidence:.2f}]")
    
    st.divider()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Product Description")
        st.write(metadata.get("description") or "No description available.")
        
        st.subheader("Product Specifications")
        # specific product details list
        st.markdown(f"""
        | Feature | Details |
        | :--- | :--- |
        | **Brand** | {metadata.get('brand') or 'N/A'} |
        | **Category** | {metadata.get('category') or 'N/A'} |
        | **Color** | {metadata.get('color') or 'N/A'} |
        | **Material** | {metadata.get('material') or 'N/A'} |
        | **Dimensions** | {metadata.get('dimensions') or 'N/A'} |
        """)
        
    with col2:
        st.subheader("Raw Data")
        with st.expander("View JSON Response", expanded=True):
            st.json(metadata)
