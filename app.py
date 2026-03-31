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
conn = sqlite3.connect('skinai_ultimate.db', check_same_thread=False)
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
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- ৩. অ্যাডভান্সড মাল্টি-রেসপন্স লজিক ---
def get_natural_response(user_query, condition):
    q = user_query.lower()
    is_bengali = bool(re.search('[\u0980-\u09FF]', q)) or any(word in q for word in ["ki", "korbo", "osud", "keno", "mane ki", "hoyeche"])
    
    # ডেটাবেস
    db = {
        'Actinic keratoses': {'cause': "সূর্যের UV রশ্মি / Sun UV Rays", 'info': "এটি প্রাক-ক্যান্সার অবস্থা।"},
        'Basal cell carcinoma': {'cause': "DNA মিউটেশন ও রোদ / DNA mutation & sun", 'info': "সাধারণ স্কিন ক্যান্সার।"},
        'Benign keratosis': {'cause': "বয়স বৃদ্ধি / Aging", 'info': "ক্ষতিকর নয় এমন গ্রোথ।"},
        'Dermatofibroma': {'cause': "ছোট ইনজুরি / Minor skin injury", 'info': "শক্ত ছোট গুটি।"},
        'Melanoma': {'cause': "তীব্র রোদ ও জেনেটিক / Intense sun & Genetics", 'info': "মারাত্মক ক্যান্সার।"},
        'Nevus': {'cause': "মেলানোসাইট গুচ্ছ / Melanocyte clusters", 'info': "সাধারণ তিল।"},
        'Vascular lesions': {'cause': "রক্তনালীর সমস্যা / Blood vessel issues", 'info': "লাল বা বেগুনি দাগ।"}
    }

    responses = []
    
    # কন্ডিশনাল চেকিং (একাধিক উত্তর জেনারেট করবে)
    if any(word in q for word in ["keno", "why", "cause", "hoyeche", "jibanu"]):
        msg = f"🟢 **Cause:** {db[condition]['cause']}" if not is_bengali else f"🟢 **কারণ:** {db[condition]['cause']}"
        responses.append(msg)
        
    if any(word in q for word in ["mane ki", "what is", "details", "ki"]):
        msg = f"🔵 **About:** {db[condition]['info']}" if not is_bengali else f"🔵 **বিস্তারিত:** {db[condition]['info']}"
        responses.append(msg)
        
    if any(word in q for word in ["osud", "medicine", "cream", "treatment"]):
        msg = "⚠️ **Note:** Do not self-medicate. See a Dr." if not is_bengali else "⚠️ **সতর্কতা:** নিজে ঔষধ না লাগিয়ে ডাক্তার দেখান।"
        responses.append(msg)

    if not responses:
        return f"I found {condition}. How can I help?" if not is_bengali else f"আপনার রিপোর্টে {condition} পাওয়া গেছে। আমি কীভাবে সাহায্য করতে পারি?"

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

# --- ৫. সাইডবার (Settings, Help, History, Login) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

with st.sidebar:
    st.markdown("### 🛠️ SkinAI Menu")
    
    with st.expander("📖 How to use"):
        st.write("1. Upload Photo\n2. Get Result\n3. Chat with AI\n4. Login to Save")

    with st.expander("⚙️ Settings"):
        st.write("Theme: Dark")
        st.write("V6.0 Stable")

    with st.expander("❓ Help"):
        st.write("Contact: wishy@advocate.com")

    st.markdown("---")

    if st.session_state.logged_in:
        st.markdown(f"👤 **User:** {st.session_state.username}")
        st.markdown("### 🕒 Recent History")
        c.execute('SELECT result, timestamp FROM history WHERE username = ? ORDER BY timestamp DESC LIMIT 5', (st.session_state.username,))
        for row in c.fetchall():
            st.caption(f"{row[1]} - {row[0]}")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
    else:
        with st.expander("🔑 Login / Sign Up"):
            u = st.text_input("Username")
            p = st.text_input("Password", type='password')
            if st.button("Login"):
                c.execute('SELECT password FROM users WHERE username = ?', (u,))
                data = c.fetchone()
                if data and check_hashes(p, data[0]):
                    st.session_state.logged_in = True
                    st.session_state.username = u
                    st.rerun()
            if st.button("Register"):
                try:
                    c.execute('INSERT INTO users VALUES (?,?)', (u, make_hashes(p)))
                    conn.commit()
                    st.success("Registered!")
                except: st.error("User exists")

# --- ৬. মেইন অ্যাপ ---
st.markdown('<h1 class="main-title">🩺 SkinAI Assistant</h1>', unsafe_allow_html=True)

if model:
    file = st.file_uploader("Choose skin image...", type=["jpg", "png", "jpeg"])
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
        
        if st.session_state.logged_in:
            if st.button("💾 Save Result"):
                ts = datetime.now().strftime("%d %b, %H:%M")
                c.execute('INSERT INTO history VALUES (?,?,?,?)', (st.session_state.username, result, conf, ts))
                conn.commit()
                st.success("Saved to History!")
        else:
            st.info("Login from sidebar to save this report.")

        # চ্যাটবট
        st.markdown("---")
        if "messages" not in st.session_state: st.session_state.messages = []
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Ask: 'Why it happened and what is the medicine?'"):
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
                    time.sleep(0.01)
                placeholder.markdown(full_txt)
                st.session_state.messages.append({"role": "assistant", "content": full_txt})
