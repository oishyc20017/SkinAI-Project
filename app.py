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

# --- ১. ডাটাবেস সেটআপ ---
conn = sqlite3.connect('skinai_pro_final.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, fullname TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS history(email TEXT, result TEXT, confidence REAL, timestamp TEXT)')
    conn.commit()

init_db()

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(p, h): return h if make_hashes(p) == h else False

# --- ২. পেজ কনফিগারেশন ও স্টাইল ---
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e3e3e3; }
    [data-testid="stSidebar"] { background-color: #1e1f20 !important; border-right: 1px solid #30363d; }
    .dev-badge { padding: 12px; border-radius: 10px; background: rgba(88, 166, 255, 0.05); border: 1px solid rgba(88, 166, 255, 0.2); text-align: center; margin-bottom: 20px; }
    .main-title { font-size: 35px; font-weight: 600; color: #c4c7c5; }
</style>
""", unsafe_allow_html=True)

# --- ৩. স্মার্ট মাল্টি-অ্যানসার লজিক (একসাথে একাধিক উত্তর) ---
def get_natural_response(user_query, condition):
    q = user_query.lower()
    is_bengali = bool(re.search('[\u0980-\u09FF]', q)) or any(word in q for word in ["ki", "korbo", "osud", "keno"])
    
    db = {
        'Actinic keratoses': {'cause': "UV Rays", 'info': "এটি একটি প্রাক-ক্যান্সার অবস্থা।"},
        'Basal cell carcinoma': {'cause': "Sun Damage", 'info': "সাধারণ চর্ম ক্যান্সার।"},
        'Benign keratosis': {'cause': "Aging", 'info': "ক্ষতিকর নয় এমন স্কিন গ্রোথ।"},
        'Dermatofibroma': {'cause': "Minor Trauma", 'info': "শক্ত ছোট টিউমার।"},
        'Melanoma': {'cause': "Genetic & UV", 'info': "মারাত্মক স্কিন ক্যান্সার।"},
        'Nevus': {'cause': "Melanocytes", 'info': "সাধারণ তিল বা আঁচিল।"},
        'Vascular lesions': {'cause': "Blood vessels", 'info': "রক্তনালীর অস্বাভাবিক দাগ।"}
    }

    responses = []
    # কন্ডিশনাল চেকিং (একাধিক উত্তর জেনারেট করবে)
    if any(word in q for word in ["keno", "why", "cause", "hoyeche"]):
        msg = f"🧬 **Cause:** {db[condition]['cause']}" if not is_bengali else f"🧬 **কারণ:** {db[condition]['cause']}"
        responses.append(msg)
    if any(word in q for word in ["ki", "what is", "mane ki", "details"]):
        msg = f"📘 **About:** {db[condition]['info']}" if not is_bengali else f"📘 **বিস্তারিত:** {db[condition]['info']}"
        responses.append(msg)
    if any(word in q for word in ["osud", "medicine", "treatment", "cream"]):
        msg = "⚠️ **Note:** Consult a doctor. No self-medication." if not is_bengali else "⚠️ **সতর্কতা:** নিজে ঔষধ না লাগিয়ে ডাক্তার দেখান।"
        responses.append(msg)

    if not responses:
        return f"I detected {condition}. How can I help?" if not is_bengali else f"রিপোর্টে {condition} এসেছে। আরও জানতে প্রশ্ন করুন।"
    
    return "\n\n".join(responses)

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

# --- ৫. সাইডবার (Gemini Layout with Multi-Option Settings) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []

with st.sidebar:
    st.markdown('<div class="dev-badge"><p style="margin:0; font-size:10px; color:#8b949e;">ARCHITECT</p><h3 style="margin:0; color:#58a6ff;">Wishy Chakma</h3></div>', unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    
    if st.session_state.logged_in:
        st.markdown(f"👋 **Hi, {st.session_state.fullname}**")
        st.caption(st.session_state.email)
        st.markdown("### 🕒 Recent History")
        c.execute('SELECT result, timestamp FROM history WHERE email = ? ORDER BY timestamp DESC LIMIT 5', (st.session_state.email,))
        for row in c.fetchall(): st.info(f"{row[0]} ({row[1]})")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
    else:
        with st.expander("👤 Login / Sign Up"):
            mode = st.radio("Choose", ["Login", "Sign Up"])
            if mode == "Sign Up":
                fn = st.text_input("Full Name")
                em = st.text_input("Gmail")
                ps = st.text_input("Password", type='password', key="s1")
                if st.button("Create Account"):
                    try:
                        c.execute('INSERT INTO users VALUES (?,?,?)', (em, fn, make_hashes(ps)))
                        conn.commit()
                        st.success("Done!")
                    except: st.error("Exists")
            else:
                em = st.text_input("Email")
                ps = st.text_input("Password", type='password', key="l1")
                if st.button("Sign In"):
                    c.execute('SELECT fullname, password FROM users WHERE email = ?', (em,))
                    data = c.fetchone()
                    if data and check_hashes(ps, data[1]):
                        st.session_state.logged_in = True
                        st.session_state.email = em
                        st.session_state.fullname = data[0]
                        st.rerun()

    st.markdown("---")
    
    # --- আপনার চাওয়া Gemini Dark মাল্টি-অপশন সেকশন ---
    with st.expander("🌙 Gemini Dark Settings"):
        theme_opt = st.selectbox("Appearance", ["Default Dark", "OLED Black", "High Contrast"])
        st.checkbox("Show Labels")
        st.checkbox("Compact Mode")
        st.write(f"Current Theme: **{theme_opt}**")

    with st.expander("❓ Help & Support"):
        st.write("Email: wishy@healthcare.ai")
        st.write("v6.5 Stable Build")

# --- ৬. মেইন অ্যাপ ---
st.markdown('<div class="main-title">SkinAI Assistant</div>', unsafe_allow_html=True)

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
        
        if st.session_state.logged_in:
            if st.button("💾 Save Result"):
                ts = datetime.now().strftime("%d %b, %H:%M")
                c.execute('INSERT INTO history VALUES (?,?,?,?)', (st.session_state.email, result, conf, ts))
                conn.commit()
                st.toast("Saved!")

        # চ্যাটবট
        st.markdown("---")
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Ask: Why it happened and what is the medicine?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                reply = get_natural_response(prompt, result)
                # টাইপিং এনিমেশন
                placeholder = st.empty()
                full_txt = ""
                for char in reply:
                    full_txt += char
                    placeholder.markdown(full_txt + "▌")
                    time.sleep(0.005)
                placeholder.markdown(full_txt)
                st.session_state.messages.append({"role": "assistant", "content": full_txt})
