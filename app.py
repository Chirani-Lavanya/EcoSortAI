import streamlit as st
from PIL import Image
import time

import google.generativeai as genai

from dotenv import load_dotenv  
import os

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

genai.configure(api_key=api_key)

# THIS CSS HERE
st.markdown("""
<style>

/* Background */
.main {
    background: linear-gradient(to right, #eef2f3, #ffffff);
}

/* Container spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Buttons */
.stButton>button {
    border-radius: 12px;
    background: linear-gradient(135deg, #4CAF50, #2E7D32);
    color: white;
    font-weight: bold;
}

/* Boxes */
.stSuccess, .stInfo, .stWarning, .stError {
    border-radius: 12px;
}

/* Headings */
h1, h2, h3 {
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

from backend.gemini_service import analyze_image

from PyPDF2 import PdfReader
from utils.parser import parse_response

# ======================================
# Load Environment Variables
# ======================================

# ======================================
# Page Configuration
# ======================================
st.set_page_config(
    page_title="EcoSort AI",
    page_icon="♻️",
    layout="centered"
)

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
    
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False  
    
# ======================================
# Load Logo (Optional)
# ======================================
try:
    logo = Image.open("assets/logo.png")
except:
    logo = None

# ======================================
# Sidebar
# ======================================
st.sidebar.title("EcoSort AI")

st.sidebar.success("🌍 SDG 12 Project")

st.sidebar.markdown("""
### EcoSort AI can identify

✅ Waste Item

✅ Waste Category

✅ Recyclability

🇱🇰 Sri Lanka Disposal Guide

🌱 Environmental Impact

♻️ Reuse Idea

💡 Eco Tip
""")

# ======================================
# Header
# ======================================

if logo:
    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.image(logo, width=180)

# 🔥 Reduce space between logo and title
st.markdown("""
<div style='text-align: center; margin-top: -30px;'>

<h1 style='
    font-size: 42px;
    font-weight: 700;
    background: linear-gradient(90deg, #2E7D32, #66BB6A);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
'>
    EcoSort AI
</h1>

<h3 style='margin-top:0; font-weight: 500; color:#333;'>
    AI-Powered Waste Sorting Assistant
</h3>

<p style='color: green; font-size:15px;'>
    🌍 Supporting SDG 12 – Responsible Consumption & Production
</p>

</div>
""", unsafe_allow_html=True)

st.info("""
### 📷 Upload a clear photo of a waste item.

EcoSort AI will:

- ♻️ Identify the waste item
- 📂 Classify the waste category
- ✅ Check if it is recyclable
- 🇱🇰 Recommend the correct disposal method in Sri Lanka
- 🌱 Suggest a reuse idea
- 💡 Provide an eco-friendly tip
""")

# ======================================
# Upload Image
# ======================================
st.markdown("### 📷 Upload Waste Image")

st.caption("Choose a JPG or PNG image of a waste item.")

uploaded_file = st.file_uploader(
    label="Choose a file",
    type=["jpg", "jpeg", "png", "pdf"],
    label_visibility="collapsed"
)

if uploaded_file is not None:

    file_type = uploaded_file.type

    # =======================
    # 📄 PDF HANDLING
    # =======================
    if "pdf" in file_type:

        reader = PdfReader(uploaded_file)
        text = ""

        for page in reader.pages:
            text += page.extract_text()

        st.subheader("📄 Extracted Text")
        st.text_area("PDF Content", text[:1000])

        if st.button("♻️ Analyze PDF", use_container_width=True):

            with st.spinner("🤖 AI is analyzing the document..."):

                start_time = time.time()
                result = analyze_image(text)
                processing_time = round(time.time() - start_time, 2)

                if result["success"]:

                    text = result["text"]

                    # 🚨 VERY IMPORTANT FIX
                    if "This is not a waste item" in text:
                        st.warning("📄 This appears to be a document, not a waste item.")
                        st.stop()

                    # ✅ ONLY PARSE IF VALID
                    parsed = parse_response(text)

                    st.success("✅ PDF Analysis Complete!")
                    st.markdown("## ♻️ Waste Analysis Report (PDF)")
                    st.divider()

                    # 📦 Waste Item
                    st.subheader("📦 Waste Item")
                    st.info(parsed.get("Waste Item", "-"))

                    # 📂 Waste Category
                    st.subheader("📂 Waste Category")
                    st.info(parsed.get("Waste Category", "-"))

                    # ♻️ Recyclable
                    st.subheader("♻️ Recyclable")
                    recyclable = parsed.get("Recyclable", "").lower()

                    if "recyclable" in recyclable or "yes" in recyclable:
                        st.success("🟢 This item is recyclable")
                    else:
                        st.error("🔴 Not recyclable")

                    # 🗑️ Disposal Guide
                    st.subheader("🗑️ Disposal Guide")
                    guide = parsed.get("Sri Lanka Disposal Guide", "")
                    if guide.strip():
                        st.info(guide)
                    else:
                        st.warning("⚠️ No disposal guidance provided")

                    # 🌱 Environmental Impact
                    st.subheader("🌱 Environmental Impact")
                    impact = parsed.get("Environmental Impact", "")
                    if impact.strip():
                        st.success(impact)
                    else:
                        st.warning("No environmental impact info available")

                    # ♻️ Reuse Idea
                    st.subheader("♻️ Reuse Idea")
                    reuse = parsed.get("Reuse Idea", "")
                    if reuse.strip():
                        st.info(reuse)
                    else:
                        st.warning("No reuse idea available")

                elif "503" in result["text"]:
                    st.warning("⚠️ High demand. Try again.")
                else:
                    st.error(result["text"])

    # =======================
    # 🖼 IMAGE HANDLING
    # =======================
    else:

        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Waste Image", use_container_width=True)

        except Exception:
            st.error("❌ Failed to open image")
            st.stop()

        if st.button("♻️ Analyze Waste", use_container_width=True):

            with st.spinner("🤖 AI is analyzing the image..."):

                start_time = time.time()
                result = analyze_image(uploaded_file)
                processing_time = round(time.time() - start_time, 2)

                if result["success"]:

                    parsed = parse_response(result["text"])

                    st.success("✅ Image Analysis Complete!")
                    
                    # 🌍 Eco Tip (TOP SECTION)
                    st.subheader("🌍 Eco Tip")
                    eco_tip = parsed.get("Eco Tip", "")
                    
                    if eco_tip.strip():
                        st.info(f"💡 {eco_tip}")
                    else:
                         waste = parsed.get("Waste Item", "").lower()
                       
                         if "plastic" in waste:
                             st.info("💡 Avoid single-use plastics. Use reusable bottles or containers.")
                         elif "paper" in waste:
                             st.info("💡 Reuse paper or switch to digital alternatives to reduce waste.")
                         else:
                             st.info("💡 Reduce, reuse, and recycle whenever possible.")

                    # 📊 METRICS DASHBOARD
                    col1, col2, col3, col4, col5 = st.columns(5)

                    with col1:
                        st.metric("🌍 Country", "Sri Lanka")

                    with col2:
                        st.metric("🎯 Goal", "SDG 12")

                    with col3:
                        st.metric("🤖 Model", result["model"])

                    with col4:
                        st.metric("⏱️ Time", f"{processing_time:.2f}s")

                    with col5:
                        confidence = parsed.get("Confidence", "Medium")

                        if not confidence or confidence == "-":
                            confidence = "Medium"

                        st.metric("📊 Confidence", confidence)

# 🌱 SUMMARY LINE
                    st.success(
                                "🌱 Proper waste disposal helps protect the environment and supports Sustainable Development Goal 12."
                                    )

                    st.caption(f"Generated using model: {result['model']}")
                    
                    st.markdown("---")
                    st.markdown("## ♻️ Waste Analysis Report")
                    st.divider()

                    st.subheader("📦 Waste Item")
                    st.info(parsed.get("Waste Item", "-").title())

                    st.subheader("📂 Waste Category")
                    st.info(parsed.get("Waste Category", "-").title())

                    st.subheader("♻️ Recyclable")
                    if parsed.get("Recyclable", "").lower() == "yes":
                        st.success("🟢 This item is recyclable")
                    else:
                        st.error("🔴 Not recyclable")

                    st.subheader("🗑️ Disposal Guide")

                    guide = parsed.get("Sri Lanka Disposal Guide")

                    # 🔥 Smart fallback instead of warning
                    if not guide or guide.strip() == "":
                        waste = parsed.get("Waste Category", "").lower()

                        if "plastic" in waste:
                            guide = "Clean, dry, and place plastics in orange recycling bins or give to local collectors."
                        elif "paper" in waste:
                            guide = "Keep paper dry and dispose via recycling bins or paper collection centers."
                        elif "glass" in waste:
                            guide = "Rinse and separate glass before sending to recycling points."
                        elif "metal" in waste:
                            guide = "Collect and hand over metal items to scrap recyclers."
                        else:
                            guide = "Follow local municipal waste disposal guidelines in Sri Lanka."

                    # ✅ Always show something
                    st.info(guide)
                       
                # 🌱 Environmental Impact
                    impact = parsed.get("Environmental Impact", "-")

                    if not impact or impact == "-":
                            impact = "Improper waste disposal can harm ecosystems and increase pollution."

                    st.markdown("### 🌱 Environmental Impact")
                    st.success(f"🌱 {impact}")


                    # ♻️ Reuse Idea
                    reuse = parsed.get("Reuse Idea", "-")

                    if not reuse or reuse == "-":
                            reuse = "Reuse this item creatively instead of discarding it."

                    st.markdown("### ♻️ Reuse Idea")
                    st.info(f"♻️ {reuse}")  

                elif "503" in result["text"]:
                    st.warning("⚠️ High demand. Try again.")
                else:
                    st.error(result["text"])
# ======================================
# About Section
# ======================================
st.divider()

with st.expander("🌍 About EcoSort AI"):

    st.write("""
EcoSort AI is an AI-powered waste sorting assistant developed to support the **United Nations Sustainable Development Goal (SDG) 12 – Responsible Consumption and Production**.

### ✨ Features

- ♻️ AI Waste Identification
- 📂 Waste Classification
- ✅ Recyclability Detection
- 🇱🇰 Sri Lanka Disposal Guide
- 🌱 Environmental Impact
- ♻️ Reuse Suggestions
- 💡 Eco Tips

### 🛠 Technologies Used

- 🐍 Python
- 🎨 Streamlit
- 🤖 Google Gemini AI
- 🖼 Pillow
""")

st.divider()

st.caption(
    "© 2026 EcoSort AI • Built with Python, Streamlit & Google Gemini AI • Supporting UN Sustainable Development Goal 12 🌍"
)