import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import gdown
import re

# 1. Page Config & Aesthetic Design
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #30363d; background: #161b22; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .dev-card {
        padding: 20px; border-radius: 12px;
        background: linear-gradient(145deg, #1e2227, #2d333b);
        text-align: center; border: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar with Developer Info
st.sidebar.markdown(f"""
    <div class="dev-card">
        <h2 style="color: #58a6ff; margin-bottom: 0;">👨‍💻 Developer</h2>
        <hr style="border: 0.5px solid #30363d;">
        <p style="font-size: 22px; margin-bottom: 5px;"><b>Wishy Chakma</b></p>
        <p style="font-size: 14px; color: #8b949e;">Skin Disease Detection AI</p>
    </div>
    """, unsafe_allow_html=True)

# 3. Smart Multilingual & Human-like Response Logic
def get_natural_response(user_query, condition):
    q = user_query.lower()
    # Bengali or Banglish detection
    is_bengali = bool(re.search('[\u0980-\u09FF]', q)) or any(word in q for word in ["ki", "korbo", "osud", "bhalo", "hobe", "ji", "ha"])

    if any(word in q for word in ["doctor", "specialist", "ডাক্তার", "dekhabo"]):
        return f"Apnar {condition}-er jonno ekjon specialist doctor dekhano sobcheye bhalo hobe. Ami ki kono help korte pari?" if not is_bengali else f"আপনার {condition}-এর জন্য একজন বিশেষজ্ঞ চর্মরোগ ডাক্তার দেখানো সবচেয়ে ভালো হবে। আমি কি আরও কোনো সাহায্য করতে পারি?"
    elif any(word in q for word in ["medicine", "cream", "ঔষধ", "osud", "lagabo"]):
        return f"Warning: Doctor-er poramorso chhara {condition}-e kono osud use korben na." if not is_bengali else f"সতর্কতা: ডাক্তারের পরামর্শ ছাড়া {condition}-এ কোনো ঔষধ বা ক্রিম ব্যবহার করবেন না।"
    elif any(word in q for word in ["care", "tips", "যত্ন", "clean"]):
        return f"Keep the area clean and avoid direct sunlight for {condition}." if not is_bengali else f"পরামর্শ: আক্রান্ত জায়গাটি পরিষ্কার রাখুন এবং রোদ থেকে দূরে থাকুন।"
    else:
        return f"I see the {condition} result. How else can I assist you with this?" if not is_bengali else f"আমি আপনার {condition} রিপোর্টটি দেখছি। এই বিষয়ে আমি আপনাকে আর কীভাবে সাহায্য করতে পারি?"

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
        
        # Chatbot Interface
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        if prompt := st.chat_input("Ask about your report..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            reply = get_natural_response(prompt, result)
            with st.chat_message("assistant"):
                st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
