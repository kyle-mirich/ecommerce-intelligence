import streamlit as st
from ui_utils import render_sidebar, render_header

st.set_page_config(
    page_title="Metadata Vision Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_header()
render_sidebar()

st.title("🔍 Metadata Vision Agent")
st.markdown("### Autonomous Multi-Agent System for Product Metadata Extraction")

st.markdown("""
Welcome to the **Metadata Vision Agent System**. This AI-powered tool uses advanced computer vision and large language models to automatically extract structured product data from various sources.

#### 🚀 Capabilities

*   **🖼️ [Image Analysis](/Image_Analysis)**: Upload product photos or use sample images to extract details like brand, color, and material.
*   **🔗 [URL Scraping](/URL_Scraping)**: Enter a product URL to scrape and parse metadata directly from the web page.
*   **📝 [Text Parsing](/Text_Parsing)**: Paste unstructured product descriptions to convert them into clean JSON.

#### 🛠️ How it Works

1.  **Select a tool** from the sidebar navigation.
2.  **Provide input** (upload a file, paste a link, or enter text).
3.  **Configure settings** in the sidebar (Model, Temperature).
4.  **View results** in structured JSON and formatted metrics.

#### 🏗️ Tech Stack

*   **LangChain v1**: Agent orchestration and tool management.
*   **Google Gemini**: Multimodal LLM for vision and text processing.
*   **Streamlit**: Interactive web interface.

👈 **Select a page from the sidebar to get started!**
""")
