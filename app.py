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

# --- 1. Database & Security (Login + Create Account) ---
conn = sqlite3.connect('skinai_pro_wishy_v7.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, fullname TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS history(email TEXT, result TEXT, timestamp TEXT)')
    conn.commit()

init_db()

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(p, h): return h if make_hashes(p) == h else False

# --- 2. Page Setup & Aesthetic Design ---
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

# Theme fix kora (Dark default)
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e3e3e3; }
    [data-testid="stSidebar"] { background-color: #1e1f20 !important; border-right: 1px solid #30363d; }
    .wishy-card {
        padding: 15px; border-radius: 12px; background: rgba(88, 166, 255, 0.1);
        border: 1px solid rgba(88, 166, 255, 0.3); text-align: center; margin-bottom: 20px;
    }
    .dev-by { font-size: 11px; color: #8b949e; letter-spacing: 1.5px; font-weight: 700; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. Smart Multi-Answer Logic ---
def get_natural_response(user_query, condition):
    q = user_query.lower()
    answers = []
    db = {
        'Melanoma': {'c': "UV Rays", 'i': "Ati ekta boro skin cancer."},
        'Nevus': {'c': "Melanocytes", 'i': "Ati sadharon til."},
        'Basal cell carcinoma': {'c': "Sun Damage", 'i': "Skin-er khoti hoyeche."}
    }
    if any(word in q for word in ["keno", "why", "cause", "hoyeche"]):
        answers.append(f"🧬 **Karone:** {db.get(condition, {}).get('c', 'UV Rays.')}")
    if any(word in q for word in ["osud", "medicine", "treatment", "cream"]):
        answers.append("⚠️ **Sotorkota:** Doctorer poramorsho chara medicine niben na.")
    return "\n\n".join(answers) if answers else f"{condition} detection hoyeche."

# --- 4. Model Loading ---
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

# --- 5. Sidebar (Logo, Branding & Correct Options) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []

with st.sidebar:
    # Logo Section
    st.markdown('<div class="wishy-card">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/2864/2864415.png", width=90)
    st.markdown('<p class="dev-by">DEVELOPED BY WISHY</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    with st.expander("❓ Help"): st.write("Upload clear photos for analysis.")
    with st.expander("⚙️ Settings"): st.write("v7.0.0 Stable")
    st.markdown("---")

    # Account Section (Login & Create Account)
    if not st.session_state.logged_in:
        with st.expander("👤 Account / Gmail Mode"):
            mode = st.radio("Choose Action", ["Login", "Create Account"])
            if mode == "Create Account":
                new_name = st.text_input("Full Name")
                new_email = st.text_input("Gmail")
                new_pw = st.text_input("Password", type='password', key="reg")
                if st.button("Sign Up"):
                    c.execute('INSERT INTO users VALUES (?,?,?)', (new_email, new_name, make_hashes(new_pw)))
                    conn.commit()
                    st.success("Account Created! Now Login.")
            else:
                email = st.text_input("Email")
                pw = st.text_input("Pass", type='password', key="log")
                if st.button("Enter"):
                    c.execute('SELECT fullname, password FROM users WHERE email = ?', (email,))
                    data = c.fetchone()
                    if data and check_hashes(pw, data[1]):
                        st.session_state.logged_in, st.session_state.fullname = True, data[0]
                        st.rerun()
    else:
        st.write(f"Logged in as: **{st.session_state.fullname}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- 6. Main App ---
st.markdown("<h1 style='color: #58a6ff;'>🩺 SkinAI Assistant</h1>", unsafe_allow_html=True)

if model:
    file = st.file_uploader("Upload Skin Image", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file).convert('RGB')
        st.image(img, width=320)
        result = "Melanoma" # Example Result
        st.success(f"Detection: {result}")

        st.markdown("---")
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Ask: 'Keno hoyeche ar osud ki?'"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                reply = get_natural_response(prompt, result)
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
