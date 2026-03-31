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

# --- ১. ডাটাবেস ও সিকিউরিটি (আগের মতোই নিখুঁত) ---
conn = sqlite3.connect('skinai_final_pro.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, fullname TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS history(email TEXT, result TEXT, timestamp TEXT)')
    conn.commit()

init_db()

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(p, h): return h if make_hashes(p) == h else False

# --- ২. পেজ কনফিগারেশন ও থিম লজিক ---
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

if 'theme' not in st.session_state: st.session_state.theme = 'Dark'

# থিম অনুযায়ী রঙ সেট করা
if st.session_state.theme == 'Dark':
    bg, txt, sb = "#0e1117", "#e3e3e3", "#1e1f20"
else:
    bg, txt, sb = "#ffffff", "#000000", "#f0f2f6"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    [data-testid="stSidebar"] {{ background-color: {sb} !important; border-right: 1px solid #30363d; }}
    .dev-badge {{ padding: 10px; border-radius: 8px; border: 1px solid #58a6ff; text-align: center; margin-bottom: 15px; }}
</style>
""", unsafe_allow_html=True)

# --- ৩. স্মার্ট মাল্টি-অ্যানসার লজিক ---
def get_natural_response(user_query, condition):
    q = user_query.lower()
    answers = []
    
    # রোগের তথ্য ভাণ্ডার
    db = {
        'Actinic keratoses': {'c': "UV Rays", 'i': "এটি প্রাক-ক্যান্সার অবস্থা।"},
        'Basal cell carcinoma': {'c': "Sun Damage", 'i': "সাধারণ স্কিন ক্যান্সার।"},
        'Melanoma': {'c': "Genetics & UV", 'i': "মারাত্মক ক্যান্সার। দ্রুত ডাক্তার দেখান।"},
        'Nevus': {'c': "Melanocytes", 'i': "সাধারণ তিল। ভয়ের কিছু নেই।"},
        'Benign keratosis': {'c': "Aging", 'i': "ক্ষতিকর নয় এমন গ্রোথ।"}
    }

    # একাধিক উত্তর চেক করা (সবগুলো উত্তর এক মেসেজে দিবে)
    if any(word in q for word in ["keno", "why", "cause", "hoyeche"]):
        answers.append(f"🧬 **কারণ:** {db.get(condition, {}).get('c', 'রোদের অতিবেগুনি রশ্মি।')}")
    
    if any(word in q for word in ["ki", "what is", "mane ki", "details"]):
        answers.append(f"📘 **বিস্তারিত:** {db.get(condition, {}).get('i', 'এটি একটি চর্মরোগ।')}")

    if any(word in q for word in ["osud", "medicine", "treatment", "cream"]):
        answers.append("⚠️ **সতর্কতা:** নিজে ঔষধ না লাগিয়ে বিশেষজ্ঞ ডাক্তার দেখান।")
    
    if not answers:
        return f"আমি {condition} শনাক্ত করেছি। আরও কিছু জানতে প্রশ্ন করুন।"

    return "\n\n".join(answers)

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

# --- ৫. সাইডবার (Gemini Layout & Multi-Option) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []

with st.sidebar:
    st.markdown(f'<div class="dev-badge"><h4 style="margin:0; color:#58a6ff;">Wishy Chakma</h4></div>', unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    # আপনার চাওয়া "Gemini Dark" অপশনটি এখন এখানে
    selected_theme = st.selectbox("🌓 Appearance", ["Dark", "Light"], index=0 if st.session_state.theme == 'Dark' else 1)
    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()

    st.markdown("---")
    
    # জিমেইল লগইন এবং সাইন-আপ
    if st.session_state.logged_in:
        st.write(f"Logged in: **{st.session_state.fullname}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
    else:
        with st.expander("👤 Sign in with Gmail Mode"):
            mode = st.radio("Choose", ["Login", "Sign Up"])
            if mode == "Sign Up":
                fn = st.text_input("Name")
                em = st.text_input("Email")
                pw = st.text_input("Pass", type='password')
                if st.button("Create"):
                    c.execute('INSERT INTO users VALUES (?,?,?)', (em, fn, make_hashes(pw)))
                    conn.commit()
                    st.success("Done!")
            else:
                em = st.text_input("Email")
                pw = st.text_input("Pass", type='password')
                if st.button("Enter"):
                    c.execute('SELECT fullname, password FROM users WHERE email = ?', (em,))
                    data = c.fetchone()
                    if data and check_hashes(pw, data[1]):
                        st.session_state.logged_in, st.session_state.email, st.session_state.fullname = True, em, data[0]
                        st.rerun()

    st.markdown("---")
    st.caption("Settings • Help • Privacy")

# --- ৬. মেইন অ্যাপ ---
st.markdown("<h1 style='color: #58a6ff;'>🩺 SkinAI Assistant</h1>", unsafe_allow_html=True)

if model:
    file = st.file_uploader("Upload Skin Image", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file).convert('RGB')
        st.image(img, width=300)
        
        # Detection
        img_res = img.resize((100, 75))
        x = np.asarray(img_res) / 255.0
        x = np.expand_dims(x, axis=0)
        pred = model.predict(x, verbose=0)
        result = classes[np.argmax(pred)]
        conf = np.max(pred) * 100
        
        st.success(f"Result: **{result}** ({conf:.2f}%)")

        # চ্যাটবট (মাল্টি-অ্যানসার দিবে)
        st.markdown("---")
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Ask: Keno hoyeche ar osud ki?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                reply = get_natural_response(prompt, result)
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
