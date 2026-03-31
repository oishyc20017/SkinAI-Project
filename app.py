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

# --- ১. ডাটাবেস সেটআপ (Gmail & Name Field সহ) ---
conn = sqlite3.connect('skinai_pro_v5.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (email TEXT PRIMARY KEY, fullname TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (email TEXT, result TEXT, confidence REAL, timestamp TEXT)''')
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
    .dev-badge { 
        padding: 10px; border-radius: 10px; background: rgba(88, 166, 255, 0.1);
        border: 1px solid #58a6ff; text-align: center; margin-bottom: 20px;
    }
    .main-title { font-size: 40px; font-weight: 800; color: #58a6ff; }
</style>
""", unsafe_allow_html=True)

# --- ৩. স্মার্ট মাল্টি-রেসপন্স লজিক (আগের মতোই থাকবে) ---
def get_natural_response(user_query, condition):
    q = user_query.lower()
    is_bengali = bool(re.search('[\u0980-\u09FF]', q)) or any(word in q for word in ["ki", "korbo", "osud", "keno"])
    
    db = {
        'Actinic keratoses': {'cause': "UV Rays", 'info': "Pre-cancer condition."},
        'Basal cell carcinoma': {'cause': "Sun Damage", 'info': "Common skin cancer."},
        'Benign keratosis': {'cause': "Aging", 'info': "Non-cancerous growth."},
        'Dermatofibroma': {'cause': "Minor Injury", 'info': "Fibrous nodule."},
        'Melanoma': {'cause': "Genetics & UV", 'info': "Dangerous cancer."},
        'Nevus': {'cause': "Melanocytes", 'info': "Normal mole."},
        'Vascular lesions': {'cause': "Blood vessels", 'info': "Red/Purple marks."}
    }

    res = []
    if any(word in q for word in ["keno", "why", "cause"]):
        res.append(f"🧬 **Cause:** {db[condition]['cause']}")
    if any(word in q for word in ["osud", "medicine", "treatment"]):
        res.append("⚠️ **Advice:** Consult a Dermatologist before using any cream.")
    
    if not res: return f"I detected {condition}. How can I help?"
    return "\n\n".join(res)

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

# --- ৫. সাইডবার (Brand Identity & Gmail Style Login) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

with st.sidebar:
    # --- Developed by Wishy ---
    st.markdown("""
        <div class="dev-badge">
            <p style="margin:0; font-size:12px; color:#8b949e;">DEVELOPED BY</p>
            <h3 style="margin:0; color:#58a6ff;">Wishy Chakma</h3>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("⚙️ Settings & Help"):
        st.write("Privacy Policy")
        st.write("Contact: wishy@healthcare.ai")

    st.markdown("---")

    if st.session_state.logged_in:
        st.markdown(f"👋 **Hi, {st.session_state.fullname}**")
        st.caption(st.session_state.email)
        
        # হিস্ট্রি সেকশন
        st.markdown("### 🕒 Your History")
        c.execute('SELECT result, timestamp FROM history WHERE email = ? ORDER BY timestamp DESC LIMIT 5', (st.session_state.email,))
        for row in c.fetchall():
            st.info(f"{row[0]} \n({row[1]})")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
    else:
        st.info("Login to save your medical history.")
        with st.expander("🔐 Account (Gmail Style)"):
            mode = st.radio("Choose", ["Login", "Sign Up"])
            
            if mode == "Sign Up":
                fname = st.text_input("Full Name")
                email = st.text_input("Gmail / Email")
                new_p = st.text_input("Password", type='password', key="s1")
                if st.button("Create Account"):
                    if "@" in email:
                        try:
                            c.execute('INSERT INTO users VALUES (?,?,?)', (email, fname, make_hashes(new_p)))
                            conn.commit()
                            st.success("Account Created!")
                        except: st.error("Email already registered.")
                    else: st.error("Invalid Email format.")
            else:
                email = st.text_input("Email")
                passwd = st.text_input("Password", type='password', key="l1")
                if st.button("Login"):
                    c.execute('SELECT fullname, password FROM users WHERE email = ?', (email,))
                    data = c.fetchone()
                    if data and check_hashes(passwd, data[1]):
                        st.session_state.logged_in = True
                        st.session_state.email = email
                        st.session_state.fullname = data[0]
                        st.rerun()
                    else: st.error("Wrong Email/Password")

# --- ৬. মেইন অ্যাপ ---
st.markdown('<h1 class="main-title">🩺 SkinAI Assistant</h1>', unsafe_allow_html=True)

if model:
    file = st.file_uploader("Upload Skin Image", type=["jpg", "png", "jpeg"])
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
            if st.button("💾 Save to My Reports"):
                ts = datetime.now().strftime("%d %b, %I:%M %p")
                c.execute('INSERT INTO history VALUES (?,?,?,?)', (st.session_state.email, result, conf, ts))
                conn.commit()
                st.success("Report saved successfully!")
        else:
            st.warning("Please login with Gmail to save reports.")

        # Chatbot
        st.markdown("---")
        if "messages" not in st.session_state: st.session_state.messages = []
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Ask about causes or treatment..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                reply = get_natural_response(prompt, result)
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
