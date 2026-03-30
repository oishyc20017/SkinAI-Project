import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import gdown
import re

# ১. হাই-এন্ড এস্থেটিক ডিজাইন (Glassmorphism & Glow Effect)
st.markdown("""
    <style>
    /* মেইন ব্যাকগ্রাউন্ড */
    .stApp {
        background: radial-gradient(circle at top right, #1a1f25, #050505);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    
    /* সাইডবার ডিজাইন */
    [data-testid="stSidebar"] {
        background: rgba(20, 25, 35, 0.8) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* কার্ড এবং বক্সের ডিজাইন */
    .dev-card {
        padding: 30px;
        border-radius: 20px;
        background: linear-gradient(145deg, #1e242c, #13171d);
        box-shadow: 10px 10px 20px #0b0e12, -5px -5px 15px #252b36;
        text-align: center;
        border: 1px solid rgba(88, 166, 255, 0.1);
        margin-bottom: 20px;
    }

    /* গ্লোয়িং টাইটেল */
    .main-title {
        font-size: 45px;
        font-weight: 800;
        background: linear-gradient(to right, #58a6ff, #bc85ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 10px 20px rgba(88, 166, 255, 0.2);
        margin-bottom: 30px;
    }

    /* চ্যাট মেসেজ স্টাইল */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
        padding: 15px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* আপলোড বক্স ডিজাইন */
    .stFileUploader {
        border: 2px dashed rgba(88, 166, 255, 0.3);
        border-radius: 15px;
        padding: 20px;
        background: rgba(88, 166, 255, 0.02);
    }
    </style>
    """, unsafe_allow_html=True)

# ২. সাইডবার (Developer Wishy Chakma)
import base64

# ইমেজকে টেক্সটে রূপান্তর করার ফাংশন (যেন সরাসরি দেখানো যায়)
def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# লোগো দেখানোর লজিক
try:
    # আপনার আপলোড করা logo.png ফাইলটি রিড করবে
    logo_base64 = get_base64_image("health.png")
    
    st.sidebar.markdown(f"""
        <div class="dev-card">
            <img src="data:image/png;base64,{logo_base64}" width="100" style="margin-bottom: 15px; filter: drop-shadow(0 0 8px rgba(88,166,255,0.5)); border-radius: 10px;">
            <h2 style="color: #58a6ff; margin-bottom: 0; font-size: 20px; letter-spacing: 1px;">INTELLIGENT CORE</h2>
            <p style="color: #8b949e; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; margin-top: 5px;">Managed by</p>
            <h1 style="color: #ffffff; font-size: 24px; margin-top: -5px; font-weight: 700;">Wishy Chakma</h1>
            <div style="height: 1px; background: linear-gradient(to right, transparent, #30363d, #58a6ff, #30363d, transparent); margin: 15px 0;"></div>
        </div>
    """, unsafe_allow_html=True)
except Exception as e:
    # যদি লোগো ফাইল না পাওয়া যায়, তবে আগের আইকনটি দেখাবে
    st.sidebar.markdown("""
        <div class="dev-card">
            <div style="font-size: 50px; margin-bottom: 10px;">💠</div>
            <h1 style="color: #ffffff; font-size: 24px;">Wishy Chakma</h1>
        </div>
    """, unsafe_allow_html=True)

# মেইন হেডার
st.markdown('<h1 class="main-title">🩺 SkinAI Intelligent Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #8b949e; margin-top: -20px; margin-bottom: 40px;">Advanced Image Analysis & Human-Centric AI Support</p>', unsafe_allow_html=True)
# ৩. হিউম্যান-লাইক স্মার্ট রেসপন্স (নতুন ও উন্নত ভার্সন)
def get_natural_response(user_query, condition):
    q = user_query.lower()
    
    # বাংলা এবং বাংলিশ কিউওয়ার্ড শনাক্ত করা
    is_bengali = bool(re.search('[\u0980-\u09FF]', q)) or \
                 any(word in q for word in ["ki", "korbo", "osud", "bhalo", "keno", "kenbo", "eita", "hoyeche"])

    # ১. রোগের কারণ বা কেন হয় (Causes)
    if any(word in q for word in ["keno", "kenbo", "why", "reason", "cause", "kijonno"]):
        if is_bengali:
            return f"দেখুন, {condition} সাধারণত বয়সের সাথে সাথে বা ত্বকের দীর্ঘদিনের অযত্নের কারণে হতে পারে। এটি বংশগতও হতে পারে। আপনার পরিবারের কি আর কারো এমন আছে?"
        return f"Usually, {condition} develops due to age, genetics, or long-term skin exposure. Do you have any family history of this?"

    # ২. ডাক্তার বা বিশেষজ্ঞ (Doctor)
    elif any(word in q for word in ["doctor", "specialist", "dekhabo", "dr"]):
        if is_bengali:
            return f"আপনার {condition}-এর জন্য একজন বিশেষজ্ঞ চর্মরোগ ডাক্তার (Dermatologist) দেখানো সবচেয়ে নিরাপদ। দেরি না করে পরামর্শ নিন। আমি কি কোনো সাহায্য করতে পারি?"
        return f"It is safest to consult a Dermatologist for your {condition}. Please seek professional advice. How can I assist further?"

    # ৩. ঔষধ বা যত্ন (Medicine/Care)
    elif any(word in q for word in ["medicine", "cream", "osud", "care", "tips"]):
        if is_bengali:
            return f"{condition}-এর জন্য নিজে নিজে কোনো ঔষধ ব্যবহার করবেন না। আক্রান্ত স্থানটি রোদে সরাসরি উন্মুক্ত না রাখাই ভালো। আপনি কি সানস্ক্রিন ব্যবহার করেন?"
        return f"Do not use any medication for {condition} without a prescription. Avoid direct sun exposure on the area. Do you use sunscreen?"

    # ৪. অন্য সব সাধারণ প্রশ্নের জন্য
    else:
        if is_bengali:
            return f"আপনার {condition} রিপোর্টটি আমি বিশ্লেষণ করেছি। ঘাবড়ানোর কিছু নেই, তবে সঠিক পরামর্শ মেনে চলা জরুরি। আপনার মনে আর কি কোনো প্রশ্ন আছে?"
        return f"I've analyzed your report for {condition}. Stay positive, but following professional advice is key. Any other questions?"
# 4. Loading Model from Google Drive (Using your new link)
@st.cache_resource
def load_my_model():
    # New File ID from your provided link 
    file_id = '1JpKXUXu_DsXK5-uq7fpgg5aDY7hBhq9h'
    model_path = 'skin_cancer_model.h5'
    url = f'https://drive.google.com/uc?id={file_id}'
    
    if not os.path.exists(model_path):
        with st.spinner('Downloading model from Google Drive... Please wait 2-3 minutes.'):
            try:
                # fuzzy=True helps bypass the large file warning page
                gdown.download(url, model_path, quiet=False, fuzzy=True)
            except Exception:
                return None
            
    if os.path.exists(model_path):
        return tf.keras.models.load_model(model_path, compile=False)
    return None

model = load_my_model()
classes = ['Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis', 'Dermatofibroma', 'Melanoma', 'Nevus', 'Vascular lesions']

# 5. Main UI Logic
st.title("🩺 SkinAI Professional Assistant")

if model is None:
    st.error("Google Drive theke model download korte somossa hochhe. Permission 'Anyone with the link' ache kina check korun.")
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
        
        st.success(f"### Detection Result: {result}")
        st.markdown("---")
        
   # চ্যাটবট ইন্টারফেস
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # আগের মেসেজগুলো স্ক্রিনে দেখানো (Aesthetic Chat Bubbles)
        for m in st.session_state.messages:
            with st.chat_message(m["role"], avatar="👤" if m["role"] == "user" else "🤖"):
                st.markdown(m["content"])

        # নতুন প্রশ্ন ইনপুট নেওয়া
        if prompt := st.chat_input("আপনার মনে কোনো প্রশ্ন থাকলে এখানে লিখুন..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
            
            # অ্যাসিস্ট্যান্টের উত্তর (Thinking Animation & Glowing Response)
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner('একটু ভাবছি...'):
                    # ভাষা বুঝে মানুষের মতো উত্তর জেনারেট করা
                    raw_reply = get_natural_response(prompt, result)
                    
                    # উত্তরের সাথে এস্থেটিক ইমোজি যোগ করা
                    is_bengali = bool(re.search('[\u0980-\u09FF]', prompt)) or any(word in prompt.lower() for word in ["ki", "korbo"])
                    if is_bengali:
                        reply = f"✨ **পরামর্শ:** {raw_reply} 🌿"
                    else:
                        reply = f"✨ **Analysis:** {raw_reply} 🌿"
                    
                    st.markdown(reply)
            
            # উত্তরটি সেভ করা যেন স্ক্রিনে থেকে যায়
            st.session_state.messages.append({"role": "assistant", "content": reply})
