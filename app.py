import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import gdown
import re

# ১. গুগল ড্রাইভের লিঙ্ক থেকে সরাসরি ডাউনলোড করার লজিক
@st.cache_resource
def load_model_from_drive():
    # নিচের লাইনে ' ' এর মাঝখানে আপনার কপি করা ড্রাইভ লিঙ্কটি বসান
    drive_url = 'https://drive.google.com/file/d/1Ey5AKBM5FA0wcj2_SMiJO1l0RWf2XIAL/view?usp=drive_link'
    
    model_path = 'skin_cancer_model.h5'
    
    if not os.path.exists(model_path):
        with st.spinner('মডেল ডাউনলোড হচ্ছে... প্রথমবার একটু সময় লাগতে পারে।'):
            # ড্রাইভ লিঙ্ক থেকে সরাসরি ডাউনলোড লিঙ্ক তৈরি
            gdown.download(url=drive_url, output=model_path, quiet=False, fuzzy=True)
    
    return tf.keras.models.load_model(model_path, compile=False)

# ২. পেজ ডিজাইন (আপনার নাম Wishy Chakma)
st.set_page_config(page_title="SkinAI - Wishy", layout="wide")

st.sidebar.markdown(f"""
    <div style="text-align: center; background: #1e2227; padding: 10px; border-radius: 10px; color: white;">
        <h3>👨‍💻 Developer</h3>
        <hr>
        <p style="font-size: 20px;"><b>Wishy Chakma</b></p>
    </div>
    """, unsafe_allow_html=True)

# ৩. অ্যাপ লজিক ও চ্যাটবট
model = load_model_from_drive()
classes = ['Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis', 'Dermatofibroma', 'Melanoma', 'Nevus', 'Vascular lesions']

st.title("🩺 SkinAI Professional Assistant")
file = st.file_uploader("আপনার ত্বকের ছবি আপলোড করুন", type=["jpg", "png", "jpeg"])

if file:
    img = Image.open(file).convert('RGB')
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, use_container_width=True)
    with col2:
        img_res = img.resize((100, 75))
        x = np.asarray(img_res) / 255.0
        x = np.expand_dims(x, axis=0)
        result = classes[np.argmax(model.predict(x, verbose=0))]
        st.success(f"রিজাল্ট: {result}")
        
        # চ্যাটবট পার্ট
        if "messages" not in st.session_state: st.session_state.messages = []
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        if prompt := st.chat_input("কীভাবে সাহায্য করতে পারি?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            # সাধারণ চ্যাটবট লজিক (বাংলিশ/বাংলা সাপোর্ট)
            reply = f"আপনার {result} সমস্যার জন্য ডার্মাটোলজিস্টের পরামর্শ নিন।" if "ki" in prompt.lower() or "doctor" in prompt.lower() else "আমি আপনার রিপোর্টটি দেখেছি।"
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()