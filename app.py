import streamlit as st
import time
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import gdown
import re

# ১. পেজ কনফিগারেশন
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

# ২. হাই-এন্ড এস্থেটিক ডিজাইন (Glassmorphism & Glow Effect)
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top right, #1a1f25, #050505);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stSidebar"] {
        background: rgba(20, 25, 35, 0.8) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    .dev-card {
        padding: 25px;
        border-radius: 20px;
        background: linear-gradient(145deg, #1e242c, #13171d);
        box-shadow: 10px 10px 20px #0b0e12, -5px -5px 15px #252b36;
        text-align: center;
        border: 1px solid rgba(88, 166, 255, 0.1);
        margin-bottom: 20px;
    }
    .main-title {
        font-size: 45px;
        font-weight: 800;
        background: linear-gradient(to right, #58a6ff, #bc85ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 10px 20px rgba(88, 166, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# ৩. সাইডবার (Developer & Disclaimer)
with st.sidebar:
    st.markdown("""
        <div class="dev-card">
            <div style="font-size: 50px; margin-bottom: 10px;">🛡️</div>
            <h2 style="color: #58a6ff; margin-bottom: 0; font-size: 22px;">Core System</h2>
            <p style="color: #8b949e; font-size: 11px; letter-spacing: 1px;">DEVELOPED BY</p>
            <h1 style="color: #ffffff; font-size: 26px; margin-top: -5px;">Wishy Chakma</h1>
            <div style="height: 1px; background: linear-gradient(to right, transparent, #58a6ff, transparent); margin: 15px 0;"></div>
            <p style="color: #58a6ff; font-style: italic; font-size: 13px;">"AI for Better Healthcare"</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar.expander("📖 How to use"):
        st.write("1. Upload a clear skin photo.\n2. Wait for AI analysis.\n3. Chat with AI about results.")
    
    st.markdown("---")
    st.warning("⚠️ Disclaimer: This AI tool is for educational purposes only. Always consult a professional Doctor.")

# ৪. টাইটেল ও হেডার
st.markdown('<h1 class="main-title">🩺 SkinAI Intelligent Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #8b949e; margin-top: -20px; margin-bottom: 40px;">Advanced Image Analysis & Human-Centric AI Support</p>', unsafe_allow_html=True)

# ৫. স্মার্ট রেসপন্স লজিক
def get_natural_response(user_query, condition):
    q = user_query.lower()
    is_bengali = bool(re.search('[\u0980-\u09FF]', q)) or any(word in q for word in ["ki", "korbo", "osud", "keno"])
    
    if any(word in q for word in ["keno", "why", "cause"]):
        res = f"{condition} সাধারণত অতিরিক্ত রোদ বা বংশগত কারণে হয়।" if is_bengali else f"{condition} is often caused by sun exposure or genetics."
    elif any(word in q for word in ["doctor", "specialist"]):
        res = "একজন চর্মরোগ বিশেষজ্ঞ দেখানো ভালো হবে।" if is_bengali else "Consult a Dermatologist soon."
    else:
        res = f"আমি আপনার {condition} রিপোর্টটি দেখছি। আর কিছু কি জানতে চান?" if is_bengali else f"I'm analyzing your {condition} report. Any other questions?"
    return res

# ৬. মডেল লোডিং
@st.cache_resource
def load_my_model():
    file_id = '1JpKXUXu_DsXK5-uq7fpgg5aDY7hBhq9h'
    model_path = 'skin_cancer_model.h5'
    if not os.path.exists(model_path):
        try: gdown.download(id=file_id, output=model_path, quiet=False, fuzzy=True)
        except: return None
    if os.path.exists(model_path):
        return tf.keras.models.load_model(model_path, compile=False)
    return None

model = load_my_model()
classes = ['Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis', 'Dermatofibroma', 'Melanoma', 'Nevus', 'Vascular lesions']

# ৭. মেইন ইউআই লজিক
if model is None:
    st.error("Model loading failed. Please check your connection.")
else:
    file = st.file_uploader("Upload Skin Image", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file).convert('RGB')
        st.image(img, width=400, caption="Uploaded Image")
        
        # Prediction
        img_res = img.resize((100, 75))
        x = np.asarray(img_res) / 255.0
        x = np.expand_dims(x, axis=0)
        pred = model.predict(x, verbose=0)
        result = classes[np.argmax(pred)]
        confidence = np.max(pred) * 100
        
        st.success(f"Detection Result: **{result}**")
        st.info(f"AI Confidence Score: **{confidence:.2f}%**")
        st.markdown("---")
        
        # চ্যাটবট
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Ask about your report..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                msg_placeholder = st.empty()
                full_res = ""
                reply = get_natural_response(prompt, result)
                for char in reply:
                    full_res += char
                    msg_placeholder.markdown(full_res + "▌")
                    time.sleep(0.01)
                msg_placeholder.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
