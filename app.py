import streamlit as st
import time
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import gdown
import re
import sqlite3
import hashlib
from datetime import datetime

# --- ১. ডাটাবেস ও সিকিউরিটি ---
conn = sqlite3.connect('skinai_final.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, fullname TEXT, password TEXT)')
    conn.commit()

init_db()

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(p, h): return h if make_hashes(p) == h else False

# --- ২. ডিজাইন ও থিম ---
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

if 'theme' not in st.session_state: st.session_state.theme = 'Dark'

bg, txt, sb, card = ("#0e1117", "#e3e3e3", "#1e1f20", "rgba(88, 166, 255, 0.1)") if st.session_state.theme == 'Dark' else ("#ffffff", "#000000", "#f0f2f6", "rgba(0, 0, 0, 0.05)")

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    [data-testid="stSidebar"] {{ background-color: {sb} !important; border-right: 1px solid #30363d; }}
    .wishy-card {{ padding: 15px; border-radius: 12px; background: {card}; border: 1px solid rgba(88, 166, 255, 0.3); text-align: center; margin-bottom: 20px; }}
    .dev-by {{ font-size: 11px; color: #8b949e; letter-spacing: 1.5px; font-weight: 700; margin-top: 10px; }}
</style>
""", unsafe_allow_html=True)

# --- ৩. এরর ফ্রি মাল্টি-অ্যানসার লজিক (Error Fixed Here) ---
def get_natural_response(user_query, condition):
    q = user_query.lower()
    answers = []
    
    # ডেটা ডিকশনারি
    db = {
        'Actinic keratoses': 'UV Rays / সূর্যের রশ্মি',
        'Melanoma': 'Genetics & UV / মারাত্মক চর্ম ক্যান্সার',
        'Nevus': 'Normal Mole / সাধারণ তিল',
        'Basal cell carcinoma': 'Sun Damage / সাধারণ স্কিন ক্যান্সার'
    }

    if any(word in q for word in ["keno", "why", "cause", "hoyeche"]):
        cause_val = db.get(condition, 'রোদের অতিবেগুনি রশ্মি।')
        answers.append(f"🧬 **কারণ:** {cause_val}")
    
    if any(word in q for word in ["osud", "medicine", "treatment", "cream"]):
        answers.append("⚠️ **সতর্কতা:** ডাক্তারের পরামর্শ ছাড়া কোনো ঔষধ ব্যবহার করবেন না।")
    
    return "\n\n".join(answers) if answers else f"আমি {condition} শনাক্ত করেছি। আরও জানতে প্রশ্ন করুন।"

# --- ৪. মডেল লোডিং ---
@st.cache_resource
def load_my_model():
    file_id = '1JpKXUXu_DsXK5-uq7fpgg5aDY7hBhq9h'
    model_path = 'skin_cancer_model.h5'
    if not os.path.exists(model_path):
        try: gdown.download(id=file_id, output=model_path, quiet=False, fuzzy=True)
        except: return None
    return tf.keras.models.load_model(model_path, compile=False) if os.path.exists(model_path) else None

model = load_my_model()
classes = ['Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis', 'Dermatofibroma', 'Melanoma', 'Nevus', 'Vascular lesions']

# --- ৫. সাইডবার ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []

with st.sidebar:
    st.markdown('<div class="wishy-card">', unsafe_allow_html=True)
    # কাজ করবে এমন একটি হেলথ/স্কিন আইকন
    st.image("https://img.icons8.com/color/96/000000/dermatology.png", width=90)
    st.markdown('<p class="dev-by">DEVELOPED BY WISHY</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    with st.expander("🌓 Appearance"):
        sel_theme = st.selectbox("Select Theme", ["Dark", "Light"], index=0 if st.session_state.theme == 'Dark' else 1)
        if sel_theme != st.session_state.theme:
            st.session_state.theme = sel_theme
            st.rerun()

    with st.expander("❓ Help"): st.write("ক্লিয়ার ছবি আপলোড করুন।")
    with st.expander("⚙️ Settings"): st.write("v6.5.4 (Fixed)")
    st.markdown("---")

    if not st.session_state.logged_in:
        with st.expander("👤 Login Mode"):
            em = st.text_input("Email")
            pw = st.text_input("Pass", type='password')
            if st.button("Enter"):
                st.session_state.logged_in, st.session_state.fullname = True, "Wishy"
                st.rerun()
    else:
        st.write(f"Hi, **{st.session_state.fullname}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- ৬. মেইন অ্যাপ ---
st.markdown("<h1 style='color: #58a6ff;'>🩺 SkinAI Assistant</h1>", unsafe_allow_html=True)

if model:
    file = st.file_uploader("Upload Skin Image", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file).convert('RGB')
        st.image(img, width=320)
        
        # Detection
        img_res = img.resize((100, 75))
        x = np.asarray(img_res) / 255.0
        x = np.expand_dims(x, axis=0)
        pred = model.predict(x, verbose=0)
        result = classes[np.argmax(pred)]
        conf = np.max(pred) * 100
        
        st.success(f"রিপোর্ট: **{result}** ({conf:.1f}%)")

        st.markdown("---")
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Ask: 'এটি কেন হয়েছে আর ঔষধ কি?'"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                reply = get_natural_response(prompt, result)
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
