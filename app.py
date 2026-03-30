import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import gdown
import re

# ১. পেজ সেটআপ
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

# ২. স্টাইল ও সাইডবার
st.markdown("""<style>.stApp { background-color: #0e1117; color: white; }</style>""", unsafe_allow_html=True)
st.sidebar.title("👨‍💻 Developer")
st.sidebar.write("Wishy Chakma")

# ৩. রেসপন্স ফাংশন
def get_natural_response(user_query, condition):
    q = user_query.lower()
    is_bengali = bool(re.search('[\u0980-\u09FF]', q)) or any(word in q for word in ["ki", "korbo"])
    if "doctor" in q or "ডাক্তার" in q:
        return f"আপনার {condition}-এর জন্য বিশেষজ্ঞ ডাক্তার দেখান।" if is_bengali else f"Consult a doctor for {condition}."
    return f"আক্রান্ত স্থান পরিষ্কার রাখুন।" if is_bengali else f"Keep the area clean."

# ৪. মডেল লোড (স্মার্ট ডাউনলোড)
@st.cache_resource
def load_my_model():
    file_id = '1Ey5AKBM5FA0wcj2_SMiJ01l0RWf2XIAL'
    model_path = 'skin_cancer_model.h5'
    if not os.path.exists(model_path):
        try:
            gdown.download(id=file_id, output=model_path, quiet=False, fuzzy=True)
        except:
            return None
    if os.path.exists(model_path):
        return tf.keras.models.load_model(model_path, compile=False)
    return None

model = load_my_model()
classes = ['Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis', 'Dermatofibroma', 'Melanoma', 'Nevus', 'Vascular lesions']

# ৫. মেইন ইন্টারফেস
st.title("🩺 SkinAI Professional Assistant")
file = st.file_uploader("Upload Skin Image", type=["jpg", "png", "jpeg"])

if file:
    img = Image.open(file).convert('RGB')
    st.image(img, width=400)
    
    if model is not None:
        img_res = img.resize((100, 75))
        x = np.asarray(img_res) / 255.0
        x = np.expand_dims(x, axis=0)
        pred = model.predict(x, verbose=0)
        result = classes[np.argmax(pred)]
        st.success(f"Result: {result}")
        
        if prompt := st.chat_input("Ask a question..."):
            reply = get_natural_response(prompt, result)
            with st.chat_message("assistant"):
                st.write(reply)
    else:
        st.error("Model not loaded. Please wait and refresh.")
