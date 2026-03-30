import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import re

# ১. পেজ সেটআপ ও স্টাইল
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

# ২. সাইডবার ডিজাইন
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
    if any(word in q for word in ["doctor", "ডাক্তার"]):
        return f"আপনার {condition}-এর জন্য দ্রুত একজন চর্মরোগ বিশেষজ্ঞ দেখান।" if is_bengali else f"Please consult a dermatologist for your {condition}."
    return f"আপনার {condition} এর জন্য আক্রান্ত স্থান পরিষ্কার রাখুন।" if is_bengali else f"Keep the area clean for {condition}."

# ৪. সরাসরি গিটহাব থেকে মডেল লোড
@st.cache_resource
def load_local_model():
    # যেহেতু ফাইলটি গিটহাবেই আছে, তাই সরাসরি লোড হবে
    if os.path.exists('skin_cancer_model.h5'):
        return tf.keras.models.load_model('skin_cancer_model.h5', compile=False)
    return None

model = load_local_model()
classes = ['Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis', 'Dermatofibroma', 'Melanoma', 'Nevus', 'Vascular lesions']

# ৫. মেইন ইন্টারফেস
st.title("🩺 SkinAI Professional Assistant")

if model is None:
    st.error("মডেল ফাইলটি (skin_cancer_model.h5) গিটহাবে পাওয়া যাচ্ছে না। দয়া করে ফাইলটি আপলোড করুন।")
else:
    file = st.file_uploader("ত্বকের ছবি আপলোড করুন", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file).convert('RGB')
        st.image(img, width=400)
        
        # ছবি প্রসেসিং ও প্রেডিকশন
        img_res = img.resize((100, 75))
        x = np.asarray(img_res) / 255.0
        x = np.expand_dims(x, axis=0)
        pred = model.predict(x, verbose=0)
        result = classes[np.argmax(pred)]
        
        st.success(f"রিপোর্ট: **{result}**")
        
        # চ্যাট ইনপুট
        if prompt := st.chat_input("কীভাবে সাহায্য করতে পারি?"):
            with st.chat_message("assistant"):
                st.write(get_natural_response(prompt, result))
