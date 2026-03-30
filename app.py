import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import gdown
import re

# ১. পেজ সেটআপ ও প্রফেশনাল ডিজাইন (Aesthetic Look)
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #30363d; background: #161b22; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .developer-box {
        padding: 20px; border-radius: 12px;
        background: linear-gradient(145deg, #1e2227, #2d333b);
        text-align: center; border: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

# ২. সাইডবার (Developer Info)
st.sidebar.markdown(f"""
    <div class="developer-box">
        <h2 style="color: #58a6ff; margin-bottom: 0;">👨‍💻 Developer</h2>
        <hr style="border: 0.5px solid #30363d;">
        <p style="font-size: 22px; margin-bottom: 5px;"><b>Wishy Chakma</b></p>
        <p style="font-size: 14px; color: #8b949e;">Skin Disease Detection AI</p>
    </div>
    """, unsafe_allow_html=True)

# ৩. হিউম্যান-লাইক স্মার্ট রেসপন্স
def get_natural_response(user_query, condition):
    q = user_query.lower()
    is_bengali = bool(re.search('[\u0980-\u09FF]', q)) or any(word in q for word in ["ki", "korbo", "osud", "bhalo"])

    if any(word in q for word in ["doctor", "specialist", "ডাক্তার"]):
        return f"আপনার {condition}-এর জন্য একজন বিশেষজ্ঞ চর্মরোগ ডাক্তার দেখানো সবচেয়ে ভালো হবে। আমি কি আরও সাহায্য করতে পারি?" if is_bengali else f"I recommend consulting a Dermatologist for your {condition}."
    elif any(word in q for word in ["care", "tips", "যত্ন"]):
        return f"✅ পরামর্শ: আক্রান্ত জায়গাটি পরিষ্কার রাখুন এবং রোদ এড়িয়ে চলুন।" if is_bengali else f"✅ Care Tips: Keep the area clean and avoid direct sunlight."
    else:
        return f"আপনার {condition} রিপোর্ট সম্পর্কে আমি আরও কী বলতে পারি? আপনি যত্ন বা ডাক্তারের বিষয়ে প্রশ্ন করতে পারেন।" if is_bengali else f"I can help with care tips for {condition}. What would you like to know?"

# ৪. গুগল ড্রাইভ থেকে বড় ফাইল ডাউনলোডের স্পেশাল লজিক
@st.cache_resource
def load_my_model():
    file_id = '1Ey5AKBM5FA0wcj2_SMiJ01l0RWf2XIAL'
    model_path = 'skin_cancer_model.h5'
    
    if not os.path.exists(model_path):
        with st.spinner('সার্ভার থেকে বড় মডেল ফাইলটি ডাউনলোড হচ্ছে... দয়া করে ২-৩ মিনিট অপেক্ষা করুন।'):
            try:
                # fuzzy=True বড় ফাইলের কনফার্মেশন পেজ হ্যান্ডেল করতে সাহায্য করে
                gdown.download(id=file_id, output=model_path, quiet=False, fuzzy=True)
            except Exception as e:
                st.error("গুগল ড্রাইভ বড় ফাইলের সিকিউরিটি স্ক্যানের কারণে ডাউনলোড ব্লক করছে।")
                return None
            
    if os.path.exists(model_path):
        return tf.keras.models.load_model(model_path, compile=False)
    return None

model = load_my_model()
classes = ['Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis', 'Dermatofibroma', 'Melanoma', 'Nevus', 'Vascular lesions']

# ৫. মেইন ইউজার ইন্টারফেস
st.title("🩺 SkinAI Professional Assistant")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📸 Upload Skin Image")
    file = st.file_uploader("", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file).convert('RGB')
        st.image(img, use_container_width=True)

with col2:
    if file:
        if model is not None:
            # প্রেডিকশন
            img_res = img.resize((100, 75))
            x = np.asarray(img_res) / 255.0
            x = np.expand_dims(x, axis=0)
            pred = model.predict(x, verbose=0)
            result = classes[np.argmax(pred)]
            
            st.success(f"### Detection Result: {result}")
            st.markdown("---")
            
            # চ্যাটবট
            if "messages" not in st.session_state:
                st.session_state.messages = []

            chat_container = st.container(height=350)
            with chat_container:
                for m in st.session_state.messages:
                    with st.chat_message(m["role"], avatar="👤" if m["role"] == "user" else "🤖"):
                        st.markdown(m["content"])

            if prompt := st.chat_input("আপনার প্রশ্নটি এখানে লিখুন..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with chat_container:
                    with st.chat_message("user", avatar="👤"): st.markdown(prompt)
                    reply = get_natural_response(prompt, result)
                    with st.chat_message("assistant", avatar="🤖"): st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
        else:
            st.warning("মডেলটি ডাউনলোড হতে পারছে না। এর কারণ গুগল ড্রাইভের 'Security Scan' বাধা।")
