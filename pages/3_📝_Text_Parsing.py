import streamlit as st
from backend import extract_metadata
from ui_utils import render_sidebar, display_results, render_header

st.set_page_config(page_title="Text Parsing - Metadata Vision", page_icon="📝", layout="wide")

render_header()
api_key, model_name, temperature = render_sidebar()

st.title("📝 Text Parsing")
st.markdown("### Extract structured metadata from raw product text descriptions")
st.markdown("---")

# Sample texts for testing
SAMPLE_TEXTS = {
    "nike": """Nike Air Zoom Pegasus 40 Running Shoes

The Nike Air Zoom Pegasus 40 is the ultimate running companion for athletes of all levels. These premium running shoes feature a breathable mesh upper in vibrant volt green with black swoosh branding and neon orange accents on the midsole.

Constructed with lightweight engineered mesh and synthetic overlays for durability, the Pegasus 40 delivers exceptional comfort mile after mile. The responsive Zoom Air cushioning in the forefoot provides energy return with every stride, while the durable rubber outsole with waffle pattern ensures reliable traction on various surfaces.

Key Features:
- Color: Volt green upper, black swoosh, neon orange midsole accents
- Material: Engineered mesh upper, synthetic overlays, rubber outsole
- Dimensions: Standard athletic fit, available in US men's sizes 7-15
- Category: Performance running shoes
- Weight: Approximately 10 oz (283g) per shoe

Perfect for daily training runs, tempo workouts, and race day performance.""",

    "chargers": """New Era Los Angeles Chargers 59FIFTY Fitted Hat - Powder Blue

Official NFL fitted cap featuring the iconic Chargers powder blue colorway. This premium structured cap showcases the team's lightning bolt logo embroidered on the front in white and gold.

Details:
- Brand: New Era
- Category: Sports fitted cap
- Color: Powder blue crown, navy blue brim
- Material: 100% polyester performance fabric
- Dimensions: 59FIFTY fitted sizing (7-8)
- Features: Flat brim, structured crown, moisture-wicking sweatband

Officially licensed by the NFL. Perfect for game day or everyday wear.""",

    "airpods": """Apple AirPods Pro (3rd Generation) - White

Experience premium wireless audio with the latest AirPods Pro featuring USB-C charging. These cutting-edge earbuds deliver unparalleled active noise cancellation and adaptive audio technology.

Specifications:
- Brand: Apple
- Category: True wireless earbuds
- Color: White
- Material: Premium plastic housing, silicone ear tips
- Dimensions: Compact charging case 1.78 x 2.39 x 0.85 inches
- Weight: 5.3g per earbud
- Battery: Up to 6 hours listening time, 30 hours with case
- Connectivity: Bluetooth 5.3

Includes USB-C charging case and multiple ear tip sizes.""",

    "lv": """Louis Vuitton Neverfull MM Monogram Canvas Tote - Brown

The iconic Neverfull MM tote bag in classic monogram canvas. This timeless piece features the signature LV monogram pattern in brown and beige with natural cowhide leather trim and golden brass hardware.

Details:
- Brand: Louis Vuitton
- Category: Luxury tote bag
- Color: Monogram brown/beige canvas with natural leather trim
- Material: Coated canvas, cowhide leather, brass hardware
- Dimensions: 12.6 x 11.4 x 6.7 inches (W x H x D)
- Closure: Open top with side laces for adjustable silhouette

Handcrafted in France. Includes detachable interior pouch.""",

    "rolex": """Rolex Submariner Date 126618LB - Blue Dial, Yellow Gold

The legendary Submariner Date in prestigious 18K yellow gold with stunning blue dial and ceramic bezel. This professional diver's watch combines luxury with uncompromising performance.

Specifications:
- Brand: Rolex
- Category: Luxury dive watch
- Color: Blue dial, blue ceramic bezel, yellow gold case and bracelet
- Material: 18K yellow gold case, Cerachrom ceramic bezel, sapphire crystal
- Dimensions: 41mm case diameter, 12.5mm thickness
- Movement: Caliber 3235 automatic, 70-hour power reserve
- Water resistance: 300 meters (1,000 feet)

Swiss-made precision timepiece with Oyster bracelet and Glidelock extension system.""",

    "polo": """Polo Ralph Lauren Big Pony Fleece Baseball Jacket - Black

Classic varsity-style jacket featuring the iconic Big Pony logo. This premium fleece jacket combines athletic heritage with contemporary streetwear style in a versatile black colorway.

Details:
- Brand: Polo Ralph Lauren
- Category: Men's fleece jacket
- Color: Black with contrasting white striping
- Material: Cotton blend fleece, ribbed collar and cuffs
- Dimensions: Regular fit, sizes S-4XL
- Features: Full zip closure, side pockets, embroidered Big Pony logo

Perfect layering piece for casual everyday wear."""
}

# Sample texts section
st.markdown("### Try a sample description")
st.markdown("Click any product below to load sample text:")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("👟 Nike Shoes", use_container_width=True, key="text_nike"):
        st.session_state['sample_text'] = SAMPLE_TEXTS["nike"]
        st.rerun()

with col2:
    if st.button("🧢 Chargers Hat", use_container_width=True, key="text_chargers"):
        st.session_state['sample_text'] = SAMPLE_TEXTS["chargers"]
        st.rerun()

with col3:
    if st.button("🎧 AirPods Pro", use_container_width=True, key="text_airpods"):
        st.session_state['sample_text'] = SAMPLE_TEXTS["airpods"]
        st.rerun()

col4, col5, col6 = st.columns(3)

with col4:
    if st.button("👜 LV Neverfull", use_container_width=True, key="text_lv"):
        st.session_state['sample_text'] = SAMPLE_TEXTS["lv"]
        st.rerun()

with col5:
    if st.button("⌚ Rolex Watch", use_container_width=True, key="text_rolex"):
        st.session_state['sample_text'] = SAMPLE_TEXTS["rolex"]
        st.rerun()

with col6:
    if st.button("🧥 Polo Jacket", use_container_width=True, key="text_polo"):
        st.session_state['sample_text'] = SAMPLE_TEXTS["polo"]
        st.rerun()

st.markdown("---")

# Text input section
st.subheader("✍️ Product Description")

# Use sample text if loaded, otherwise empty
if 'sample_text' in st.session_state and st.session_state['sample_text']:
    default_text = st.session_state['sample_text']
    st.info(f"Loaded sample: {default_text.split(chr(10))[0][:60]}...")
else:
    default_text = ""

text_input = st.text_area("Enter or edit product description", value=default_text, height=300, placeholder="Paste product details here...")

st.markdown("---")

if st.button("🔍 Parse Text", type="primary", use_container_width=True):
    if not text_input:
        st.warning("Please enter some text")
    elif not api_key:
        st.error("Please configure API Key first.")
    else:
        with st.spinner("📝 Agent parsing text..."):
            try:
                metadata = extract_metadata(
                    input_data=text_input,
                    input_type="text",
                    model_name=model_name,
                    temperature=temperature
                )
                display_results(metadata)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
