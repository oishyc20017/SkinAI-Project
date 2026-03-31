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

# --- ১. ডাটাবেস ও ডিজাইন ---
conn = sqlite3.connect('skinai_pro_final.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, fullname TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS history(email TEXT, result TEXT, timestamp TEXT)')
    conn.commit()

init_db()

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(p, h): return h if make_hashes(p) == h else False

# --- ২. পেজ সেটআপ ও এস্থেটিক ডিজাইন ---
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

if 'theme' not in st.session_state: st.session_state.theme = 'Dark'

# থিম অনুযায়ী কালার প্যালেট
if st.session_state.theme == 'Dark':
    bg, txt, sb, card = "#0e1117", "#e3e3e3", "#1e1f20", "rgba(88, 166, 255, 0.1)"
else:
    bg, txt, sb, card = "#ffffff", "#000000", "#f0f2f6", "rgba(0, 0, 0, 0.05)"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    [data-testid="stSidebar"] {{ background-color: {sb} !important; border-right: 1px solid #30363d; }}
    
    /* Wishy's Aesthetic Brand Card */
    .wishy-card {{
        padding: 15px; border-radius: 12px; background: {card};
        border: 1px solid rgba(88, 166, 255, 0.3); text-align: center; margin-bottom: 20px;
    }}
    .wishy-name {{
        background: linear-gradient(45deg, #58a6ff, #bc85ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 22px; font-weight: 800; margin: 0;
    }}
    .dev-by {{ font-size: 11px; color: #8b949e; letter-spacing: 1px; margin-top: 5px; font-weight: 600; }}
</style>
""", unsafe_allow_html=True)

# --- ৩. স্মার্ট মাল্টি-অ্যানসার লজিক ---
def get_natural_response(user_query, condition):
    q = user_query.lower()
    answers = []
    
    db = {
        'Actinic keratoses': {'c': "UV Rays", 'i': "এটি প্রাক-ক্যান্সার অবস্থা।"},
        'Melanoma': {'c': "Genetics & UV", 'i': "মারাত্মক চর্ম ক্যান্সার।"},
        'Nevus': {'c': "Melanocytes", 'i': "সাধারণ তিল।"},
        'Basal cell carcinoma': {'c': "Sun Damage", 'i': "সাধারণ স্কিন ক্যান্সার।"}
    }

    if any(word in q for word in ["keno", "why", "cause", "hoyeche"]):
        answers.append(f"🧬 **কারণ:** {db.get(condition, {}).get('c', 'রোদের অতিবেগুনি রশ্মি।')}")
    
    if any(word in q for word in ["osud", "medicine", "treatment", "cream"]):
        answers.append("⚠️ **সতর্কতা:** ডাক্তারের পরামর্শ ছাড়া কোনো ঔষধ ব্যবহার করবেন না।")
    
    if not answers: return f"আমি {condition} শনাক্ত করেছি। আরও জানতে প্রশ্ন করুন।"
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

# --- ৫. সাইডবার (Gemini Layout - All Options Restored) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []

with st.sidebar:
    # --- Aesthetic Wishy Card ---
    st.markdown("""
        <div class="wishy-card">
            <h1 class="wishy-name">WISHY</h1>
            <p class="dev-by">DEVELOPED BY WISHY</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    # ১. থিম অপশন
    with st.expander("🌓 Appearance"):
        selected_theme = st.selectbox("Select Theme", ["Dark", "Light"], index=0 if st.session_state.theme == 'Dark' else 1)
        if selected_theme != st.session_state.theme:
            st.session_state.theme = selected_theme
            st.rerun()

    # ২. হেল্প অপশন
    with st.expander("❓ Help"):
        st.write("• Upload clear skin images.")
        st.write("• Ask about causes or treatments.")

    # ৩. সেটিংস অপশন
    with st.expander("⚙️ Settings"):
        st.write("Version: 6.5.0")
        st.write("Status: Secure")

    st.markdown("---")

    # লগইন সেকশন
    if not st.session_state.logged_in:
        with st.expander("👤 Login / Sign Up"):
            em = st.text_input("Gmail")
            pw = st.text_input("Password", type='password')
            if st.button("Enter"):
                st.session_state.logged_in, st.session_state.fullname, st.session_state.email = True, "Wishy", em
                st.rerun()
    else:
        st.write(f"Logged in: **{st.session_state.fullname}**")
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
        st.success(f"Result: **{result}** ({conf:.1f}%)")

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
