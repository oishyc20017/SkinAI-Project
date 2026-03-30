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
    /* ১. মেইন থিম ও ব্যাকগ্রাউন্ড */
    .stApp {
        background: radial-gradient(circle at top right, #1a1f25, #050505);
        color: #e0e0e0;
    }
    
    /* ২. চ্যাট ইনপুট বক্সের লাল ভাব দূর করা (Fix for Red Border) */
    div[data-baseweb="input"] {
        border: 1px solid rgba(88, 166, 255, 0.2) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease-in-out;
    }

    /* ইনপুট বক্সে ক্লিক করলে নীল গ্লো হবে */
    div[data-baseweb="input"]:focus-within {
        border-color: #58a6ff !important;
        box-shadow: 0 0 15px rgba(88, 166, 255, 0.4) !important;
    }

    /* লাল এন্টার বাটন নীল করা */
    button[kind="primaryChatInput"] {
        background-color: #58a6ff !important;
        color: white !important;
        border-radius: 50% !important;
    }

    /* ৩. সাইডবার ডিজাইন */
    [data-testid="stSidebar"] {
        background: rgba(20, 25, 35, 0.9) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* ৪. চ্যাট মেসেজ স্টাইল */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
        margin-bottom: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

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
st.sidebar.markdown("""
    <div class="dev-card">
        <div style="font-size: 50px; margin-bottom: 10px;">🛡️</div>
        <h2 style="color: #58a6ff; margin-bottom: 0; font-size: 24px;">Core System</h2>
        <p style="color: #8b949e; font-size: 14px; letter-spacing: 1px;">DEVELOPED BY</p>
        <h1 style="color: #ffffff; font-size: 28px; margin-top: -10px;">Wishy Chakma</h1>
        <div style="height: 2px; background: linear-gradient(to right, transparent, #58a6ff, transparent); margin: 20px 0;"></div>
        <p style="color: #58a6ff; font-style: italic;">"AI for Better Healthcare"</p>
    </div>
    """, unsafe_allow_html=True)

# মেইন হেডার
st.markdown('<h1 class="main-title">🩺 SkinAI Intelligent Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #8b949e; margin-top: -20px; margin-bottom: 40px;">Advanced Image Analysis & Human-Centric AI Support</p>', unsafe_allow_html=True)
# ৩. হিউম্যান-লাইক স্মার্ট রেসপন্স (নতুন ও উন্নত ভার্সন)
def get_natural_response(user_query, condition):
    q = user_query.lower()
    is_bengali = bool(re.search('[\u0980-\u09FF]', q)) or any(word in q for word in ["ki", "korbo", "osud", "bhalo", "hobe", "ami", "amar"])

    if any(word in q for word in ["doctor", "specialist", "ডাক্তার", "dekhabo", "treatment"]):
        if is_bengali:
            return f"দেখুন, {condition} বিষয়টি অবহেলা করা ঠিক হবে না। আমি আপনাকে পরামর্শ দেব দ্রুত একজন চর্মরোগ বিশেষজ্ঞ (Dermatologist) দেখাতে। আপনি কি আপনার এলাকার ভালো ডাক্তারের খোঁজ চাচ্ছেন?"
        return f"I understand your concern about {condition}. It's really important to consult a dermatologist for a professional checkup. Would you like me to help find a specialist near you?"

    elif any(word in q for word in ["medicine", "cream", "ঔষধ", "osud", "lagabo", "tablet"]):
        if is_bengali:
            return f"আমি আপনার কষ্টটা বুঝতে পারছি, কিন্তু {condition}-এর জন্য হুট করে কোনো ঔষধ বা ক্রিম লাগানো বিপদজনক হতে পারে। ডাক্তার না দেখিয়ে কিছু ব্যবহার করবেন না প্লিজ। আপনি কি আক্রান্ত স্থানে কোনো ব্যথা অনুভব করছেন?"
        return f"I know you're looking for relief, but applying medicine for {condition} without a prescription can be risky. Are you experiencing any pain or itching right now?"

    elif any(word in q for word in ["care", "tips", "যত্ন", "clean", "ki vabe"]):
        if is_bengali:
            return f"অবশ্যই! {condition} থাকলে জায়গাটি সব সময় পরিষ্কার আর শুকনো রাখার চেষ্টা করুন। রোদ থেকে দূরে থাকুন আর জায়গাটা একদম ঘষবেন না। আর কিছু কি জানতে চান?"
        return f"Of course! For {condition}, keep the area clean and dry. Avoid direct sunlight and try not to scratch it. Is there anything else you're worried about?"

    else:
        if is_bengali:
            return f"আমি আপনার {condition} রিপোর্টটি মন দিয়ে দেখেছি। ঘাবড়াবেন না, সঠিক সময়ে চিকিৎসা নিলে এটি সেরে যায়। এই বিষয়ে আপনার মনে আর কোনো প্রশ্ন থাকলে আমাকে নির্দ্বিধায় বলতে পারেন।"
        return f"I've carefully analyzed your report for {condition}. Don't worry too much; with proper care, it's manageable. Feel free to ask me anything else on your mind."
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
