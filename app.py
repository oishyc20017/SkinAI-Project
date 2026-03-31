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

# ১. ডাটাবেস ও সিকিউরিটি সেটআপ
conn = sqlite3.connect('skinai_pro.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS history(username TEXT, result TEXT, confidence REAL, timestamp TEXT)')
    conn.commit()

init_db()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text: return hashed_text
    return False

# ২. পেজ কনফিগারেশন ও ডিজাইন
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle at top right, #1a1f25, #050505); color: #e0e0e0; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background: rgba(20, 25, 35, 0.9) !important; backdrop-filter: blur(15px); }
    .main-title { font-size: 45px; font-weight: 800; background: linear-gradient(to right, #58a6ff, #bc85ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
</style>
""", unsafe_allow_html=True)

# ৩. স্মার্ট রেসপন্স লজিক
def get_natural_response(user_query, condition):
    q = user_query.lower()
    is_bengali = bool(re.search('[\u0980-\u09FF]', q)) or any(word in q for word in ["ki", "korbo", "osud", "keno", "mane ki", "hoyeche", "jibanu", "shudhu"])
    
    disease_info = {
        'Actinic keratoses': {'bn': "এটি সূর্যের অতিবেগুনি রশ্মির (UV Rays) প্রভাবে হয়। এটি কোনো জীবাণু নয়, বরং কোষের DNA ক্ষতি।", 'en': "Caused by long-term UV exposure damaging skin cell DNA. Not caused by germs."},
        'Basal cell carcinoma': {'bn': "এটি অতিরিক্ত রোদের কারণে হওয়া কোষে অস্বাভাবিক বৃদ্ধি। এটি সংক্রামক নয়।", 'en': "Unusual growth in basal cells due to sun exposure. Not contagious."},
        'Benign keratosis': {'bn': "এটি বয়সের সাথে কেরাটিন কোষ জমার কারণে হয়। কোনো সংক্রমণ নয়।", 'en': "Buildup of keratinocytes related to aging. Not an infection."},
        'Dermatofibroma': {'bn': "এটি ছোট আঘাত বা পোকার কামড়ের প্রতি ত্বকের রিঅ্যাকশন।", 'en': "A reaction to minor trauma like insect bites. Not caused by a pathogen."},
        'Melanoma': {'bn': "এটি মেলানোসাইট কোষে মিউটেশনের কারণে হয়। দ্রুত ডাক্তার দেখানো জরুরি।", 'en': "Mutations in pigment cells triggered by UV rays. Consult a doctor immediately."},
        'Nevus': {'bn': "এটি রঞ্জক কোষের প্রাকৃতিক গুচ্ছ (তিল)। এটি কোনো সংক্রমণ নয়।", 'en': "Natural clusters of pigment cells. Not an infection."},
        'Vascular lesions': {'bn': "এটি রক্তনালীর অস্বাভাবিক গঠনের কারণে হয়। হরমোন বা জন্মগত হতে পারে।", 'en': "Abnormal blood vessel formation. Can be hormonal or congenital."}
    }

    if any(word in q for word in ["shudhu 7ta", "shudu 7", "3k", "3000", "only 7"]):
        if is_bengali: return "বিশ্বে ৩০০০+ চর্মরোগ থাকলেও আমি সবচেয়ে গুরুত্বপূর্ণ ৭টি ক্যান্সার ও টিউমার শনাক্ত করতে পারি যা জীবন বাঁচাতে সাহায্য করবে।"
        return "Though there are 3000+ skin diseases, I focus on the 7 most critical ones to help save lives."
    elif any(word in q for word in ["keno", "jibanu", "pathogen", "cause"]):
        info = disease_info.get(condition, {})
        return info.get('bn' if is_bengali else 'en', "Please consult a specialist.")
    else:
        if is_bengali: return f"আপনার রিপোর্টে {condition} শনাক্ত হয়েছে। আপনি কি এর কারণ বা প্রতিকার সম্পর্কে জানতে চান?"
        return f"I have detected {condition}. Would you like to know more about its causes or treatment?"

# ৪. মডেল লোডিং
@st.cache_resource
def load_my_model():
    file_id = '1JpKXUXu_DsXK5-uq7fpgg5aDY7hBhq9h'
    model_path = 'skin_cancer_model.h5'
    if not os.path.exists(model_path):
        try: gdown.download(id=file_id, output=model_path, quiet=False, fuzzy=True)
        except: return None
    if os.path.exists(model_path): return tf.keras.models.load_model(model_path, compile=False)
    return None

model = load_my_model()
classes = ['Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis', 'Dermatofibroma', 'Melanoma', 'Nevus', 'Vascular lesions']

# ৫. সাইডবার ও লগইন কন্ট্রোল
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'show_login' not in st.session_state: st.session_state.show_login = False

with st.sidebar:
    st.markdown('<h2 style="color: #58a6ff;">🛡️ Core System</h2>', unsafe_allow_html=True)
    if st.session_state.logged_in:
        st.success(f"Logged in as: {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
        
        st.markdown("### 📜 Your Past History")
        c.execute('SELECT result, timestamp FROM history WHERE username = ? ORDER BY timestamp DESC', (st.session_state.username,))
        for row in c.fetchall():
            st.info(f"{row[0]}\n({row[1]})")
    else:
        st.info("Login to save your scan history.")
        if st.button("Go to Login/Sign-up"):
            st.session_state.show_login = not st.session_state.show_login

# ৬. লগইন ইন্টারফেস (যদি ইউজার চায়)
if st.session_state.show_login and not st.session_state.logged_in:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.subheader("🔑 Authentication")
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            u = st.text_input("User", key="l_user")
            p = st.text_input("Pass", type='password', key="l_pass")
            if st.button("Login"):
                c.execute('SELECT password FROM users WHERE username = ?', (u,))
                data = c.fetchone()
                if data and check_hashes(p, data[0]):
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.session_state.show_login = False
                    st.rerun()
                else: st.error("Wrong credentials")
        with tab2:
            nu = st.text_input("New User", key="s_user")
            np = st.text_input("New Pass", type='password', key="s_pass")
            if st.button("Create Account"):
                try:
                    c.execute('INSERT INTO users VALUES (?,?)', (nu, make_hashes(np)))
                    conn.commit()
                    st.success("Success! Please login.")
                except: st.error("User exists.")

# ৭. মেইন অ্যাপ্লিকেশন (Public Access)
st.markdown('<h1 class="main-title">🩺 SkinAI Intelligent Assistant</h1>', unsafe_allow_html=True)

if model:
    file = st.file_uploader("Upload Skin Image (No login required)", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file).convert('RGB')
        st.image(img, width=400)
        
        # Prediction
        img_res = img.resize((100, 75))
        x = np.asarray(img_res) / 255.0
        x = np.expand_dims(x, axis=0)
        pred = model.predict(x, verbose=0)
        result = classes[np.argmax(pred)]
        conf = np.max(pred) * 100
        
        st.success(f"Detection: **{result}** ({conf:.2f}%)")
        
        # History Save Button
        if not st.session_state.logged_in:
            if st.button("💾 Save this result to my History"):
                st.warning("Please login first to save results.")
                st.session_state.show_login = True
                st.rerun()
        else:
            if st.button("💾 Save result now"):
                ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                c.execute('INSERT INTO history VALUES (?,?,?,?)', (st.session_state.username, result, conf, ts))
                conn.commit()
                st.balloons()
                st.success("Saved to your profile!")

        # Chat Section
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
