import streamlit as st
from backend import extract_metadata
from backend.utils import process_uploaded_image
from ui_utils import render_sidebar, display_results, render_header

st.set_page_config(page_title="Image Analysis - Metadata Vision", page_icon="🖼️", layout="wide")

render_header()
api_key, model_name, temperature = render_sidebar()

st.title("🖼️ Image Analysis")
st.markdown("### Extract structured metadata from product images using Gemini Vision")
st.markdown("---")

# Upload section with improved layout
st.subheader("📤 Upload Image")
uploaded_file = st.file_uploader("Choose a product image", type=["png", "jpg", "jpeg", "webp"], help="Supported formats: PNG, JPG, JPEG, WEBP")

# Sample images section
st.markdown("### Or try a sample image")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("👟 Nike Shoes", use_container_width=True):
        st.session_state['sample_image_url'] = "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=800"
        st.session_state['sample_image_name'] = "Nike Shoes"
        st.session_state['use_sample'] = True
        st.rerun()

with col2:
    if st.button("🧢 Chargers Hat", use_container_width=True):
        st.session_state['sample_image_url'] = "https://fanatics.frgimages.com/los-angeles-chargers/mens-new-era-powder-blue-los-angeles-chargers-main-59fifty-fitted-hat_ss5_p-200014675+pv-1+u-dmsslgvnlaiusulnecrq+v-u0eoemh5udtbq03ss0xj.jpg?_hv=2&w=1018"
        st.session_state['sample_image_name'] = "Los Angeles Chargers Hat"
        st.session_state['use_sample'] = True
        st.rerun()

with col3:
    if st.button("👜 LV Purse", use_container_width=True):
        st.session_state['sample_image_url'] = "https://us.louisvuitton.com/images/is/image/lv/1/PP_VP_L/louis-vuitton-neverfull-mm--M46987_PM2_Front%20view.png?wid=1090&hei=1090"
        st.session_state['sample_image_name'] = "Louis Vuitton Purse"
        st.session_state['use_sample'] = True
        st.rerun()

col4, col5, col6 = st.columns(3)

with col4:
    if st.button("🕶️ Ray-Ban", use_container_width=True):
        st.session_state['sample_image_url'] = "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=800"
        st.session_state['sample_image_name'] = "Ray-Ban Sunglasses"
        st.session_state['use_sample'] = True
        st.rerun()

with col5:
    if st.button("⌚ Rolex Watch", use_container_width=True):
        st.session_state['sample_image_url'] = "https://cdn2.jomashop.com/media/catalog/product/cache/0ee3019724ce73007b606b54ba535a23/r/o/rolex-submariner-blue-dial-18k-yellow-gold-oyster-bracelet-automatic-mens-watch-126618lbblso.jpg?width=546&height=546"
        st.session_state['sample_image_name'] = "Rolex Watch"
        st.session_state['use_sample'] = True
        st.rerun()

with col6:
    if st.button("🧥 Polo Jacket", use_container_width=True):
        st.session_state['sample_image_url'] = "https://images.dxl.com/is/image/CasualMale/pN4068polo_black?fmt=pjpeg&pscan=auto&op_sharpen=0&resMode=sharp2&op_usm=0.5%2C1%2C5%2C0&iccEmbed=0&printRes=72&layer=0&format=pjpg&auto=avif&qlt=75&bgc=FFFFFF&wid=1024"
        st.session_state['sample_image_name'] = "Polo Ralph Lauren Jacket"
        st.session_state['use_sample'] = True
        st.rerun()

st.markdown("---")

# Analyze button
analyze_btn = st.button("🔍 Analyze Image", type="primary", use_container_width=True, disabled=not (uploaded_file or st.session_state.get('use_sample', False)))
        
# Handle sample image state
if 'use_sample' not in st.session_state:
    st.session_state['use_sample'] = False
    
if uploaded_file:
    st.session_state['use_sample'] = False
    image_source = uploaded_file
    image_type = "upload"
elif st.session_state.get('use_sample', False):
    # Use randomly selected sample from session state
    image_source = st.session_state.get('sample_image_url', "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800")
    image_type = "url"
    sample_name = st.session_state.get('sample_image_name', 'Product')
    st.info(f"Using sample image: {sample_name}")
else:
    image_source = None

if image_source:
    st.markdown("---")
    st.subheader("📸 Preview")

    # Center the image using columns
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.image(image_source, caption="Product Image", use_container_width=True)

    if analyze_btn:
        if not api_key:
            st.error("Please configure API Key first.")
        else:
            with st.spinner("🤖 Vision Agent analyzing image..."):
                try:
                    # Process based on source type
                    if image_type == "upload":
                        image_data = process_uploaded_image(image_source)
                        final_input = image_data["data"]
                    else:
                        final_input = image_source

                    # Extract
                    metadata = extract_metadata(
                        input_data=final_input,
                        input_type="image",
                        model_name=model_name,
                        temperature=temperature
                    )
                    
                    display_results(metadata)
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
