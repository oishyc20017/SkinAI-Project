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
conn = sqlite3.connect('skinai_v4.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS history(username TEXT, result TEXT, confidence REAL, timestamp TEXT)')
    conn.commit()

init_db()

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(p, h): return h if make_hashes(p) == h else False

# --- ২. পেজ সেটআপ ও ডিজাইন ---
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    .main-title { font-size: 40px; font-weight: 800; color: #58a6ff; }
    .sidebar-text { font-size: 14px; color: #8b949e; }
</style>
""", unsafe_allow_html=True)

# --- ৩. স্মার্ট রেসপন্স লজিক ---
def get_natural_response(user_query, condition):
    q = user_query.lower()
    is_bengali = bool(re.search('[\u0980-\u09FF]', q)) or any(word in q for word in ["ki", "korbo", "osud", "keno", "mane ki"])
    
    disease_info = {
        'Actinic keratoses': {'bn': "এটি সূর্যের অতিবেগুনি রশ্মির প্রভাবে হয়। এটি কোনো জীবাণু নয়, কোষের DNA ক্ষতি।", 'en': "Caused by UV exposure. Not a germ-based infection."},
        'Basal cell carcinoma': {'bn': "এটি অস্বাভাবিক কোষ বৃদ্ধি। রোদে পোড়া থেকে এটি হতে পারে।", 'en': "Abnormal basal cell growth, usually from sun damage."},
        'Benign keratosis': {'bn': "এটি বয়সের সাথে হওয়া সাধারণ স্কিন গ্রোথ। ক্ষতিকর নয়।", 'en': "Non-cancerous skin growth related to aging."},
        'Dermatofibroma': {'bn': "এটি ছোট ইনজুরি বা পোকামাকড়ের কামড় থেকে হতে পারে।", 'en': "Small, non-cancerous bumps from minor skin injury."},
        'Melanoma': {'bn': "এটি মারাত্মক স্কিন ক্যান্সার। দ্রুত বিশেষজ্ঞ ডাক্তার দেখান।", 'en': "Serious skin cancer. See a dermatologist immediately."},
        'Nevus': {'bn': "এটি সাধারণ তিল বা জন্মদাগ। চিন্তার কিছু নেই।", 'en': "Common moles or birthmarks. Usually harmless."},
        'Vascular lesions': {'bn': "এটি রক্তনালীর সমস্যার কারণে হয়।", 'en': "Caused by abnormalities in blood vessels."}
    }

    if any(word in q for word in ["shudhu 7ta", "only 7", "3000"]):
        return "বিশ্বে ৩০০০+ রোগ থাকলেও আমি ৭টি গুরুত্বপূর্ণ ক্যান্সার ও টিউমার নিয়ে কাজ করি।" if is_bengali else "I focus on 7 critical types out of 3,000+ conditions."
    elif any(word in q for word in ["keno", "jibanu", "cause", "why"]):
        info = disease_info.get(condition, {})
        return info.get('bn' if is_bengali else 'en', "Please consult a pro.")
    else:
        return f"আপনার রিপোর্টে {condition} শনাক্ত হয়েছে। আরও কিছু জানতে চান?" if is_bengali else f"I found {condition}. Any more questions?"

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

# --- ৫. সাইডবার ইন্টারফেস (Gemini Style) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

with st.sidebar:
    st.markdown("### 🛠️ Wishy's Core System")
    
    # How to use (Expandable)
    with st.expander("📖 How to use"):
        st.write("1. Upload photo\n2. Get Result\n3. Save if logged in.")

    # Settings & Help (Expandable)
    with st.expander("⚙️ Settings"):
        st.write("Profile Privacy")
        st.write("Language: BN/EN")

    with st.expander("❓ Help & Support"):
        st.write("Email: support@skinai.pro")
        st.write("User Manual")

    st.markdown("---")

    # হিস্ট্রি (শুধুমাত্র লগইন থাকলে দেখাবে)
    if st.session_state.logged_in:
        st.markdown("### 🕒 Recent History")
        c.execute('SELECT result, timestamp FROM history WHERE username = ? ORDER BY timestamp DESC LIMIT 5', (st.session_state.username,))
        rows = c.fetchall()
        if rows:
            for row in rows:
                st.caption(f"📅 {row[1]}")
                st.info(f"{row[0]}")
        else:
            st.write("No history found.")
        
        st.markdown("---")
        st.write(f"Logged in as: **{st.session_state.username}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
    else:
        # লগইন অপশন (একদম নিচে)
        with st.expander("🔑 Login / Sign Up"):
            u = st.text_input("User")
            p = st.text_input("Pass", type='password')
            col1, col2 = st.columns(2)
            if col1.button("Login"):
                c.execute('SELECT password FROM users WHERE username = ?', (u,))
                data = c.fetchone()
                if data and check_hashes(p, data[0]):
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.rerun()
            if col2.button("Register"):
                try:
                    c.execute('INSERT INTO users VALUES (?,?)', (u, make_hashes(p)))
                    conn.commit()
                    st.success("Registered!")
                except: st.error("User exists.")

# --- ৬. মেইন অ্যাপ ---
st.markdown('<h1 class="main-title">🩺 SkinAI Assistant</h1>', unsafe_allow_html=True)
st.write("Get AI-powered diagnosis for 7 major skin conditions. Searching is open for all.")

if model:
    file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file).convert('RGB')
        st.image(img, width=400)
        
        # Detection
        img_res = img.resize((100, 75))
        x = np.asarray(img_res) / 255.0
        x = np.expand_dims(x, axis=0)
        pred = model.predict(x, verbose=0)
        result = classes[np.argmax(pred)]
        conf = np.max(pred) * 100
        
        st.success(f"Detection Result: **{result}** ({conf:.2f}%)")
        
        # Save Button (Conditional)
        if st.session_state.logged_in:
            if st.button("💾 Save this to History"):
                ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                c.execute('INSERT INTO history VALUES (?,?,?,?)', (st.session_state.username, result, conf, ts))
                conn.commit()
                st.success("Result saved to your profile!")
        else:
            st.warning("Want to save this? Please Login from the sidebar.")

        # Chatbot Section
        st.markdown("---")
        if "messages" not in st.session_state: st.session_state.messages = []
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Ask about your report..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                reply = get_natural_response(prompt, result)
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
