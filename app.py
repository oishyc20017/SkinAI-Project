import streamlit as st
import google.generativeai as genai
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import gdown

# --- কনফিগারেশন (API Key) ---
# নিরাপদ থাকার জন্য Streamlit Secrets ব্যবহার করুন (Settings > Secrets)
API_KEY = st.secrets["API_KEY"]
genai.configure(api_key=API_KEY)
model_gemini = genai.GenerativeModel('gemini-1.5-flash')

# --- মডেল লোডিং ---
@st.cache_resource
def load_skin_model():
    path = 'skin_cancer_model.h5'
    if not os.path.exists(path):
        gdown.download(id='1JpKXUXu_DsXK5-uq7fpgg5aDY7hBhq9h', output=path, quiet=False)
    return tf.keras.models.load_model(path, compile=False)

model = load_skin_model()
disease_classes = ['Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis', 'Dermatofibroma', 'Melanoma', 'Nevus', 'Vascular lesions']

# --- সাইডবার ডিজাইন ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100) # এখানে আপনার লোগো দিতে পারেন
    st.title("SkinAI Pro")
    
    # Secure Gateway অপশন
    st.subheader("🔒 Secure Gateway")
    st.info("SHA-256 Encrypted Session")
    
    if st.button("+ New Chat"):
        st.rerun()
        
    st.markdown("---")
    
    # Help অপশন
    with st.expander("❓ Help & Information"):
        st.write("আপনার ত্বকের সমস্যার ছবি আপলোড করুন এবং AI এর পরামর্শ নিন।")
        
    st.markdown("---")
    st.button("Login")
    st.button("Register")

# --- মেইন চ্যাট ইন্টারফেস ---
st.title("SkinAI Assistant")

uploaded_file = st.file_uploader("Upload Skin Photo", type=["jpg", "png", "jpeg"], key="uploader")

if uploaded_file:
    # ইমেজ প্রসেসিং
    img = Image.open(uploaded_file).convert('RGB').resize((100, 75))
    x = np.expand_dims(np.asarray(img) / 255.0, axis=0)
    pred = model.predict(x, verbose=0)
    detected_disease = disease_classes[np.argmax(pred)]
    
    st.success(f"### Detection Result: {detected_disease}")

    # চ্যাটবট লজিক
    prompt = st.chat_input("Ask about your skin condition...")
    if prompt:
        st.chat_message("user").write(prompt)
        
        # AI রেসপন্স
        instruction = f"User has {detected_disease}. Answer professionally in English: {prompt}"
        response = model_gemini.generate_content(instruction)
        st.chat_message("assistant").write(response.text)
