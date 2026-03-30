import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import gdown
import re

# ১. পেজ সেটআপ ও ডিজাইন (Wishy Chakma)
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #30363d; background: #161b22; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .developer-box { padding: 20px; border-radius: 12px; background: #1e2227; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ২. সাইডবার
st.sidebar.markdown(f"""
    <div class="developer-box">
        <h2 style="color: #58a6ff;">👨‍💻 Developer</h2>
        <p style="font-size: 20px;"><b>Wishy Chakma</b></p>
    </div>
    """, unsafe_allow_html=True)

# ৩. হিউম্যান-লাইক স্মার্ট রেসপন্স
def get_natural_response(user_query, condition):
    q = user_query.lower()
    is_bengali = bool(re.search('[\u0980-\u09FF]', q)) or any(word in q for word in ["ki", "korbo", "osud"])
    if any(word in q for word in ["doctor", "specialist", "ডাক্তার"]):
        return f"আপনার {condition}-এর জন্য একজন বিশেষজ্ঞ চর্মরোগ ডাক্তার দেখানো সবচেয়ে ভালো হবে।" if is_bengali else f"I recommend consulting a Dermatologist for your {condition}."
    return f"আপনার {condition} এর জন্য আক্রান্ত স্থানটি পরিষ্কার রাখুন।" if is_bengali else f"Keep the area clean for {condition}."

# ৪. বড় ফাইল ডাউনলোডের স্পেশাল লজিক (Security Scan Bypass)
@st.cache_resource
def load_my_model():
    file_id = '1Ey5AKBM5FA0wcj2_SMiJ01l0RWf2XIAL'
    model_path = 'skin_cancer_model.h5'
    
    if not os.path.exists(model_path):
        with st.spinner('বড় ফাইলটি ড্রাইভ থেকে নামানো হচ্ছে... ১-২ মিনিট সময় দিন।'):
            try:
                # 'fuzzy=True' বড় ফাইলের কনফার্মেশন পেজ বাইপাস করে
                gdown.download(id=file_id, output=model_path, quiet=False, fuzzy=True)
            except Exception:
                st.error("ডাউনলোড এখনো বাধাগ্রস্ত হচ্ছে।")
                return None
            
    if os.path.exists(model_path):
        return tf.keras.models.load_model(model_path, compile=False)
    return None

model = load_my_model()
classes = ['Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis', 'Dermatofibroma', 'Melanoma', 'Nevus', 'Vascular lesions']

# ৫. মেইন ইউজার ইন্টারফেস
st.title("🩺 SkinAI Professional Assistant")
file = st.file_uploader("ত্বকের ছবি আপলোড করুন", type=["jpg", "png", "jpeg"])

if file:
    img = Image.open(file).convert('RGB')
    st.image(img, width=400)
    
    if model is not None:
        img_res = img.resize((100, 75))
        x = np.asarray(img_res) / 255.0
        x = np.expand_dims(x, axis=0)
        pred = model.predict(x, verbose=0)
        result = classes[np.argmax(pred)]
        
        st.success(f"রিপোর্ট: {result}")
        
        if prompt := st.chat_input("প্রশ্ন করুন..."):
            with st.chat_message("assistant"):
                st.write(get_natural_response(prompt, result))
    else:
        st.warning("মডেল লোড হয়নি। দয়া করে কিছুক্ষণ অপেক্ষা করে রিবুট দিন।")
                    st.session_state.messages.append({"role": "assistant", "content": reply})
        else:
            st.warning("মডেলটি ডাউনলোড হতে পারছে না। এর কারণ গুগল ড্রাইভের 'Security Scan' বাধা।")
