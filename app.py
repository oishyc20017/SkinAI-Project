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
    is_bengali = bool(re.search('[\u0980-\u09FF]', q)) or any(word in q for word in ["ki", "korbo", "osud", "bhalo", "keno", "eita"])

    # ১. রোগের কারণ বা কেন হয় (Causes)
    if any(word in q for word in ["keno", "why", "reason", "kijonno", "cause"]):
        if is_bengali:
            return f"দেখুন, {condition} হওয়ার পেছনে সাধারণত অতিরিক্ত সূর্যের আলো (UV Rays), বংশগত কারণ বা ত্বকের অযত্ন দায়ী থাকতে পারে। তবে সঠিক কারণ নিশ্চিত হতে বায়োপসি করা প্রয়োজন। আপনি কি রোদে বেশি সময় কাটান?"
        return f"Usually, {condition} is caused by excessive UV exposure, genetics, or long-term skin irritation. However, a biopsy is needed for a definitive reason. Do you spend a lot of time in the sun?"

    # ২. ডাক্তার বা বিশেষজ্ঞ (Doctor)
    elif any(word in q for word in ["doctor", "specialist", "ডাক্তার", "dekhabo"]):
        if is_bengali:
            return f"আপনার {condition}-এর জন্য একজন বিশেষজ্ঞ চর্মরোগ ডাক্তার (Dermatologist) দেখানো সবচেয়ে ভালো হবে। দেরি করবেন না প্লিজ। আমি কি ডাক্তার খোঁজার তথ্য দেব?"
        return f"I recommend consulting a Dermatologist as soon as possible for your {condition}. Shall I provide more information on how to find one?"

    # ৩. ঔষধ বা ক্রিম (Medicine)
    elif any(word in q for word in ["medicine", "cream", "ঔষধ", "osud", "lagabo"]):
        if is_bengali:
            return f"আমি বুঝতে পারছি আপনি সমাধান খুঁজছেন, কিন্তু {condition}-এ ডাক্তারের পরামর্শ ছাড়া কোনো ক্রিম লাগানো উল্টো ফল দিতে পারে। কোনো কিছু লাগানোর আগে বিশেষজ্ঞের মতামত নিন। আপনার কি জায়গাটিতে চুলকানি হচ্ছে?"
        return f"I understand you're looking for a cure, but applying anything to {condition} without a prescription can be dangerous. Have you noticed any itching or bleeding?"

    # ৪. লক্ষণ বা সিম্পটম (Symptoms)
    elif any(word in q for word in ["symptom", "lokkhon", "problem", "sign"]):
        if is_bengali:
            return f"{condition}-এর সাধারণ লক্ষণ হলো ত্বকের ওই জায়গায় রঙের পরিবর্তন, ক্ষত বা ফোলা ভাব। আপনার ক্ষেত্রে কি নতুন কোনো পরিবর্তন লক্ষ্য করেছেন?"
        return f"Common signs of {condition} include changes in skin color, non-healing sores, or bumps. Have you noticed any recent changes in that area?"

    # ৫. সাধারণ কুশল বিনিময় বা ডিফল্ট
    else:
        if is_bengali:
            return f"আপনার {condition} রিপোর্টটি আমি গুরুত্ব দিয়ে দেখেছি। ঘাবড়াবেন না, সঠিক সময়ে চিকিৎসা নিলে এটি পুরোপুরি সেরে যায়। এই বিষয়ে আপনার মনে আর কোনো নির্দিষ্ট প্রশ্ন আছে?"
        return f"I've carefully analyzed your report for {condition}. Stay positive, it's manageable with professional help. Do you have any specific concerns about this?"
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
