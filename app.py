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

# --- ১. ডাটাবেস ও সিকিউরিটি (আপনার জিমেইল লগইন সিস্টেম) ---
conn = sqlite3.connect('skinai_pro_wishy_final.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, fullname TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS history(email TEXT, result TEXT, timestamp TEXT)')
    conn.commit()

init_db()

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(p, h): return h if make_hashes(p) == h else False

# --- ২. পেজ সেটআপ ও এস্থেটিক ডিজাইন (Gemini Dark) ---
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

if 'theme' not in st.session_state: st.session_state.theme = 'Dark'

if st.session_state.theme == 'Dark':
    bg, txt, sb, card = "#0e1117", "#e3e3e3", "#1e1f20", "rgba(88, 166, 255, 0.1)"
else:
    bg, txt, sb, card = "#ffffff", "#000000", "#f0f2f6", "rgba(0, 0, 0, 0.05)"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    [data-testid="stSidebar"] {{ background-color: {sb} !important; border-right: 1px solid #30363d; }}
    .wishy-card {{
        padding: 15px; border-radius: 12px; background: {card};
        border: 1px solid rgba(88, 166, 255, 0.3); text-align: center; margin-bottom: 20px;
    }}
    .dev-by {{ font-size: 11px; color: #8b949e; letter-spacing: 1.5px; font-weight: 700; margin-top: 10px; }}
</style>
""", unsafe_allow_html=True)

# --- ৩. স্মার্ট মাল্টি-অ্যানসার লজিক (আপনার সেই বিশেষ ফিচার) ---
def get_natural_response(user_query, condition):
    q = user_query.lower()
    answers = []
    
    db = {
        'Actinic keratoses': {'c': "UV Rays", 'i': "এটি প্রাক-ক্যান্সার অবস্থা।"},
        'Melanoma': {'c': "Genetics & UV", 'i': "মারাত্মক চর্ম ক্যান্সার।"},
        'Nevus': {'c': "Melanocytes", 'i': "সাধারণ তিল।"},
        'Basal cell carcinoma': {'c': "Sun Damage", 'i': "সাধারণ স্কিন ক্যান্সার।"}
    }

    # একাধিক উত্তর চেক করা (সবগুলো এক মেসেজে দিবে)
    if any(word in q for word in ["keno", "why", "cause", "hoyeche"]):
        answers.append(f"🧬 **কারণ:** {db.get(condition, {{}}).get('c', 'রোদের অতিবেগুনি রশ্মি।')}")
    
    if any(word in q for word in ["osud", "medicine", "treatment", "cream", "solution"]):
        answers.append("⚠️ **সতর্কতা:** ডাক্তারের পরামর্শ ছাড়া কোনো ঔষধ ব্যবহার করবেন না। একজন ডার্মাটোলজিস্ট দেখান।")
    
    if any(word in q for word in ["ki", "what is", "mane ki", "details"]):
        answers.append(f"📘 **বিস্তারিত:** {db.get(condition, {{}}).get('i', 'এটি একটি সাধারণ চর্মরোগ।')}")

    if not answers:
        return f"আমি {condition} শনাক্ত করেছি। আরও বিস্তারিত বা প্রতিকার জানতে প্রশ্ন করুন।"

    return "\n\n".join(answers)

# --- ৪. আপনার অরিজিনাল মডেল লোডিং (Cache সহ) ---
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

# --- ৫. সাইডবার (Logo, Developed by Wishy & All Options) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []

with st.sidebar:
    # --- লোগো এবং ব্র্যান্ডিং ---
    st.markdown('<div class="wishy-card">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/2864/2864415.png", width=90)
    st.markdown('<p class="dev-by">DEVELOPED BY WISHY</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    # ৩টি ড্রপডাউন অপশন (যা আপনি চেয়েছিলেন)
    with st.expander("🌓 Appearance"):
        sel_theme = st.selectbox("Select Theme", ["Dark", "Light"], index=0 if st.session_state.theme == 'Dark' else 1)
        if sel_theme != st.session_state.theme:
            st.session_state.theme = sel_theme
            st.rerun()

    with st.expander("❓ Help"):
        st.write("• ক্লিয়ার ছবি আপলোড করুন।")
        st.write("• কেন হয়েছে বা ঔষধ কি—তা জিজ্ঞেস করুন।")

    with st.expander("⚙️ Settings"):
        st.write("Build: v6.5.3 (Stable)")
        st.write("Database: Connected")

    st.markdown("---")

    # লগইন ও সাইন-আপ সেকশন
    if not st.session_state.logged_in:
        with st.expander("👤 Login / Sign Up"):
            mode = st.radio("Choose", ["Login", "Sign Up"])
            if mode == "Sign Up":
                fn = st.text_input("Full Name")
                em = st.text_input("Gmail")
                pw = st.text_input("Pass", type='password', key="s1")
                if st.button("Create Account"):
                    c.execute('INSERT INTO users VALUES (?,?,?)', (em, fn, make_hashes(pw)))
                    conn.commit()
                    st.success("Done!")
            else:
                em = st.text_input("Email")
                pw = st.text_input("Pass", type='password', key="l1")
                if st.button("Enter"):
                    c.execute('SELECT fullname, password FROM users WHERE email = ?', (em,))
                    data = c.fetchone()
                    if data and check_hashes(pw, data[1]):
                        st.session_state.logged_in, st.session_state.email, st.session_state.fullname = True, em, data[0]
                        st.rerun()
    else:
        st.write(f"Hi, **{st.session_state.fullname}**")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

# --- ৬. মেইন অ্যাপ ইন্টারফেস ---
st.markdown("<h1 style='color: #58a6ff;'>🩺 SkinAI Assistant</h1>", unsafe_allow_html=True)

if model:
    file = st.file_uploader("আপনার ত্বকের ছবি এখানে দিন...", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file).convert('RGB')
        st.image(img, width=320)
        
        # Detection (মডেল প্রেডিকশন)
        img_res = img.resize((100, 75))
        x = np.asarray(img_res) / 255.0
        x = np.expand_dims(x, axis=0)
        pred = model.predict(x, verbose=0)
        result = classes[np.argmax(pred)]
        conf = np.max(pred) * 100
        
        st.success(f"রিপোর্ট: **{result}** ({conf:.1f}%)")

        st.markdown("---")
        # চ্যাট হিস্ট্রি
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        # স্মার্ট চ্যাট ইনপুট
        if prompt := st.chat_input("Ask: 'এটি কেন হয়েছে আর ঔষধ কি?'"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                reply = get_natural_response(prompt, result)
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
