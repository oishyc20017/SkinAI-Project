import streamlit as st
import time
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import gdown
import sqlite3

# --- ১. ডাটাবেস ও ডিজাইন ---
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e3e3e3; }
    [data-testid="stSidebar"] { background-color: #1e1f20 !important; border-right: 1px solid #30363d; }
    
    /* Branding Card Style */
    .brand-card {
        padding: 20px; border-radius: 15px; background: rgba(88, 166, 255, 0.05);
        border: 1px solid rgba(88, 166, 255, 0.2); text-align: center; margin-bottom: 25px;
    }
    .wishy-tag {
        font-size: 12px; color: #58a6ff; letter-spacing: 2px; 
        font-weight: 800; margin-top: 10px; text-transform: uppercase;
        font-family: 'Courier New', Courier, monospace;
    }
    /* Social Buttons Style */
    .social-btn {
        display: flex; align-items: center; justify-content: center;
        padding: 10px; border-radius: 8px; margin-bottom: 10px; font-weight: bold; cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# --- ২. স্মার্ট মাল্টি-ল্যাঙ্গুয়েজ এআই ইঞ্জিন ---
def get_advanced_response(query, condition):
    # Thinking Process Animation
    with st.status("SkinAI is analyzing your queries...", expanded=False) as status:
        time.sleep(2)
        status.update(label="Analysis Done!", state="complete")
    
    q = query.lower()
    answers = []
    
    # Knowledge Base (মানুষের মতো ডিটেইলড উত্তর)
    if any(word in q for word in ["keno", "why", "cause", "হলো"]):
        answers.append(f"🧬 **কারণ:** {condition} মূলত অতিবেগুনি রশ্মি বা ত্বকের কোষের অস্বাভাবিক পরিবর্তনের কারণে হয়।")
    
    if any(word in q for word in ["osud", "medicine", "ঔষধ", "solution"]):
        answers.append(f"⚠️ **পরামর্শ:** {condition}-এর জন্য কোনো স্টেরয়েড ক্রিম নিজে থেকে ব্যবহার করবেন না। বিশেষজ্ঞ ডাক্তার দেখানো জরুরি।")
    
    if any(word in q for word in ["ki", "what", "details", "রোগ"]):
        answers.append(f"📘 **বিস্তারিত:** এটি একটি {condition} জনিত সমস্যা। সময়মতো চিকিৎসা করলে এটি নিয়ন্ত্রণ করা সম্ভব।")

    if not answers:
        return f"আমি আপনার রিপোর্টে **{condition}** পেয়েছি। আপনি কি এর কারণ, ঔষধ বা অন্য কিছু জানতে চান? আমি সব ল্যাঙ্গুয়েজ বুঝি।"

    return "\n\n---\n\n".join(answers)

# --- ৩. অরিজিনাল এআই মডেল লোডিং ---
@st.cache_resource
def load_full_model():
    file_id = '1JpKXUXu_DsXK5-uq7fpgg5aDY7hBhq9h'
    model_path = 'skin_cancer_model.h5'
    if not os.path.exists(model_path):
        try: gdown.download(id=file_id, output=model_path, quiet=False, fuzzy=True)
        except: return None
    return tf.keras.models.load_model(model_path, compile=False)

model = load_full_model()
classes = ['Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis', 'Dermatofibroma', 'Melanoma', 'Nevus', 'Vascular lesions']

# --- ৪. সাইডবার (Logo, Branding, Login, Menus) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []
if 'last_report' not in st.session_state: st.session_state.last_report = "None"

with st.sidebar:
    # ১ & ২: লোগো এবং স্টাইলিশ Wishy ট্যাগ
    st.markdown('<div class="brand-card">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3591/3591147.png", width=90)
    st.markdown('<p class="wishy-tag">⭐ Developed by Wishy ⭐</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    # ৩: সেটিংস ও হেল্প অপশন
    with st.expander("⚙️ Settings"):
        st.write("Privacy: Secure")
        st.write("Version: v11.0 Stable")
    with st.expander("❓ Help"):
        st.write("ক্লিয়ার ছবি আপলোড করে যেকোনো প্রশ্ন করুন।")

    st.markdown("---")

    # ৪ & ৫: লগইন এবং সোশ্যাল মিডিয়া অপশন
    if not st.session_state.logged_in:
        with st.expander("👤 Account / Create Account"):
            choice = st.radio("Choose", ["Login", "Sign Up"])
            st.markdown('<div style="background:white; color:black; padding:8px; border-radius:5px; text-align:center; margin-bottom:5px; cursor:pointer;">🔵 Continue with Facebook</div>', unsafe_allow_html=True)
            st.markdown('<div style="background:white; color:black; padding:8px; border-radius:5px; text-align:center; margin-bottom:10px; cursor:pointer;">🔴 Continue with Gmail</div>', unsafe_allow_html=True)
            
            email = st.text_input("Gmail Address")
            if st.button("Continue"):
                if "@" in email:
                    st.session_state.logged_in = True
                    st.session_state.user = email
                    st.rerun()
    else:
        st.info(f"Hi, **{st.session_state.user}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- ৫. মেইন কন্টেন্ট ---
st.title("🩺 SkinAI Assistant")

if st.session_state.logged_in:
    # ৬: ছবি দেখে রোগ শনাক্তকরণ
    file = st.file_uploader("Upload Skin Photo", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file).convert('RGB')
        st.image(img, width=350)
        
        if model:
            img_res = img.resize((100, 75))
            x = np.asarray(img_res) / 255.0
            x = np.expand_dims(x, axis=0)
            pred = model.predict(x, verbose=0)
            st.session_state.last_report = classes[np.argmax(pred)]
            conf = np.max(pred) * 100
            st.success(f"রিপোর্ট: **{st.session_state.last_report}** ({conf:.1f}%)")

    st.markdown("---")
    
    # ৭, ৮, ৯: মানুষের মতো সব ধরনের প্রশ্নের উত্তর দেওয়া
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("যেকোনো কিছু জিজ্ঞাসা করুন (বাংলা/English)..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            response = get_advanced_response(prompt, st.session_state.last_report)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.warning("আপনার প্রোজেক্ট শুরু করতে সাইডবার থেকে লগইন করুন।")
