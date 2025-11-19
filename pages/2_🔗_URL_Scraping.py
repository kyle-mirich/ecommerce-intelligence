import streamlit as st
from backend import extract_metadata
from ui_utils import render_sidebar, display_results, render_header

st.set_page_config(page_title="URL Scraping - Metadata Vision", page_icon="🔗", layout="wide")

render_header()
api_key, model_name, temperature = render_sidebar()

st.title("🔗 URL Scraping")
st.markdown("### Extract structured metadata from product URLs")
st.markdown("---")

# URL input section
st.subheader("🌐 Enter URL")
url_input = st.text_input("Product URL", placeholder="https://example.com/product/123")

# Sample URLs section
st.markdown("### Or try a sample URL")
st.markdown("Click any product below to auto-fill the URL:")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🎧 AirPods Pro 3", use_container_width=True, key="url_airpods"):
        st.session_state['selected_url'] = "https://www.apple.com/shop/buy-airpods/airpods-pro-3"
        st.rerun()

with col2:
    if st.button("👜 LV Neverfull", use_container_width=True, key="url_lv"):
        st.session_state['selected_url'] = "https://us.louisvuitton.com/eng-us/products/neverfull-mm-monogram-nvprod5350101v/M46987"
        st.rerun()

with col3:
    if st.button("⌚ Rolex Submariner", use_container_width=True, key="url_rolex"):
        st.session_state['selected_url'] = "https://www.jomashop.com/rolex-submariner-blue-dial-18k-yellow-gold-oyster-bracelet-automatic-mens-watch-126618lbblso.html"
        st.rerun()

with col4:
    if st.button("🧥 Polo Jacket", use_container_width=True, key="url_polo"):
        st.session_state['selected_url'] = "https://www.dxl.com/p/polo-ralph-lauren-big-pony-fleece-baseball-jacket-n4068?swatch=POLO%20BLACK"
        st.rerun()

# Handle selected URL from session state
if 'selected_url' in st.session_state and st.session_state['selected_url']:
    url_input = st.session_state['selected_url']
    st.info(f"Selected URL: {url_input[:80]}..." if len(url_input) > 80 else f"Selected URL: {url_input}")

st.markdown("---")

if st.button("🔍 Scrape URL", type="primary", use_container_width=True):
    if not url_input:
        st.warning("Please enter a URL")
    elif not api_key:
        st.error("Please configure API Key first.")
    else:
        with st.spinner("🕷️ Agent scraping page and extracting metadata... (this may take 30-60 seconds)"):
            try:
                metadata = extract_metadata(
                    input_data=url_input,
                    input_type="url",
                    model_name=model_name,
                    temperature=temperature
                )
                display_results(metadata)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
