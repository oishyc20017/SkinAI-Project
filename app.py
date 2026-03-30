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
    .stButton>button { background-color: #238636; color: white; border-radius: 8px; }
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

# ৩. স্মার্ট ল্যাঙ্গুয়েজ ও হিউম্যান-লাইক রেসপন্স
def get_natural_response(user_query, condition):
    q = user_query.lower()
    # বাংলা বা বাংলিশ শনাক্তকরণ
    is_bengali = bool(re.search('[\u0980-\u09FF]', q)) or any(word in q for word in ["ki", "korbo", "osud", "bhalo", "hobe", "ji", "ha"])

    if any(word in q for word in ["doctor", "specialist", "ডাক্তার", "dekhabo"]):
        return f"আপনার {condition}-এর জন্য একজন বিশেষজ্ঞ চর্মরোগ ডাক্তার দেখানো সবচেয়ে ভালো হবে। আমি কি ডাক্তার খোঁজার তথ্য দেব?" if is_bengali else f"I recommend consulting a Dermatologist for your {condition}. Shall I provide more info?"
    elif any(word in q for word in ["medicine", "cream", "ঔষধ", "osud", "lagabo"]):
        return f"⚠️ **সতর্কতা:** ডাক্তারের পরামর্শ ছাড়া {condition}-এ কোনো ঔষধ বা ক্রিম ব্যবহার করবেন না।" if is_bengali else f"⚠️ **Warning:** Do not apply any medicine for {condition} without a doctor's advice."
    elif any(word in q for word in ["care", "tips", "যত্ন", "clean"]):
        return f"✅ **পরামর্শ:** আক্রান্ত জায়গাটি পরিষ্কার রাখুন, ঘষবেন না এবং রোদ থেকে দূরে থাকুন।" if is_bengali else f"✅ **Care Tips:** Keep the area clean, avoid scratching, and stay out of direct sunlight."
    else:
        return f"আপনার {condition} রিপোর্ট সম্পর্কে আর কী জানতে চান? আমি যত্ন বা ডাক্তারের বিষয়ে বলতে পারি।" if is_bengali else f"I can help with care tips or doctor recommendations for {condition}. What would you like to know?"

# ৪. গুগল ড্রাইভ থেকে মডেল লোড (স্মার্ট ডাউনলোড পদ্ধতি)
@st.cache_resource
def load_my_model():
    file_id = '1Ey5AKBM5FA0wcj2_SMiJ01l0RWf2XIAL'
    # Direct Download Links (৩টি আলাদা বিকল্প)
    urls = [
        f'https://drive.google.com/uc?id={file_id}',
        f'https://drive.google.com/uc?export=download&id={file_id}',
        f'https://drive.google.com/open?id={file_id}'
    ]
    model_path = 'skin_cancer_model.h5'
    
    if not os.path.exists(model_path):
        with st.spinner('সার্ভার থেকে মডেল লোড হচ্ছে... এটি ১-২ মিনিট সময় নিতে পারে।'):
            success = False
            for url in urls:
                try:
                    gdown.download(url, model_path, quiet=False, fuzzy=True)
                    if os.path.exists(model_path):
                        success = True
                        break
                except:
                    continue
            if not success:
                st.error("ডাউনলোড ব্যর্থ হয়েছে। গুগল ড্রাইভের লিঙ্কটি সরাসরি অ্যাক্সেস করতে পারছে না।")
                return None
            
    return tf.keras.models.load_model(model_path, compile=False)

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
        st.image(img, use_container_width=True, caption="আপলোড করা ছবি")

with col2:
    if file:
        if model is not None:
            # প্রেডিকশন লজিক
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
            st.warning("মডেলটি লোড হতে পারেনি। পেজটি রিফ্রেশ (Refresh) করে দেখুন।")
