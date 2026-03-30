import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import gdown
import re

# ১. পেজ সেটআপ
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

# ২. সাইডবার (Wishy Chakma)
st.sidebar.markdown(f"""
    <div style="text-align: center; background: #1e2227; padding: 20px; border-radius: 10px;">
        <h2 style="color: #00d4ff;">👨‍💻 Developer</h2>
        <hr>
        <p style="color: white; font-size: 20px;"><b>Wishy Chakma</b></p>
    </div>
    """, unsafe_allow_html=True)

# ৩. স্মার্ট রেসপন্স ফাংশন
def get_natural_response(user_query, condition):
    q = user_query.lower()
    is_bengali = bool(re.search('[\u0980-\u09FF]', q)) or any(word in q for word in ["ki", "korbo", "osud"])
    if "doctor" in q or "ডাক্তার" in q:
        return f"আপনার {condition}-এর জন্য একজন বিশেষজ্ঞ ডাক্তার দেখান।" if is_bengali else f"Consult a doctor for {condition}."
    return f"আমি আপনার {condition} রিপোর্টটি পেয়েছি। আর কী সাহায্য করতে পারি?" if is_bengali else f"I see the {condition} result. How else can I help?"

# ৪. মডেল লোড করার নিরাপদ পদ্ধতি (ERROR FIX)
@st.cache_resource
def load_my_model():
    model_path = 'skin_cancer_model.h5'
    file_id = '1Ey5AKBM5FA0wcj2_SMiJ01l0RWf2XIAL'
    url = f'https://drive.google.com/uc?id={file_id}'
    
    if not os.path.exists(model_path):
        try:
            with st.spinner('মডেল লোড হচ্ছে...'):
                gdown.download(url, model_path, quiet=False)
        except:
            return None
            
    if os.path.exists(model_path):
        return tf.keras.models.load_model(model_path, compile=False)
    return None

# মডেল লোড করা
model = load_my_model()
classes = ['Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis', 'Dermatofibroma', 'Melanoma', 'Nevus', 'Vascular lesions']

# ৫. মেইন অ্যাপ ইন্টারফেস
st.title("🩺 SkinAI Professional Assistant")
file = st.file_uploader("আপনার ত্বকের ছবি আপলোড করুন", type=["jpg", "png", "jpeg"])

if file:
    img = Image.open(file).convert('RGB')
    st.image(img, width=400)
    
    # মডেল চেক (NAME ERROR সমাধান)
    if model is not None:
        img_res = img.resize((100, 75))
        x = np.asarray(img_res) / 255.0
        x = np.expand_dims(x, axis=0)
        pred = model.predict(x, verbose=0)
        result = classes[np.argmax(pred)]
        
        st.success(f"শনাক্ত করা হয়েছে: {result}")
        
        # চ্যাট বক্স
        if prompt := st.chat_input("প্রশ্ন করুন..."):
            with st.chat_message("assistant"):
                st.write(get_natural_response(prompt, result))
    else:
        st.error("দুঃখিত, সার্ভার থেকে মডেল ফাইলটি পাওয়া যাচ্ছে না। আপনার গুগল ড্রাইভের লিঙ্ক বা পারমিশনটি পুনরায় চেক করুন।")
