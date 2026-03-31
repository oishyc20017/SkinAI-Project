import streamlit as st
import time
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import gdown
import sqlite3
import hashlib

# --- ১. ডাটাবেস ও সিকিউরিটি ---
conn = sqlite3.connect('skinai_wishy_v14.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS chat_history(email TEXT, role TEXT, content TEXT)')
    conn.commit()

init_db()

def make_hash(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hash(p, h): return h if make_hash(p) == h else False

# --- ২. এস্থেটিক ডিজাইন ---
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e3e3e3; }
    [data-testid="stSidebar"] { background-color: #1e1f20 !important; border-right: 1px solid #30363d; }
    .brand-card {
        padding: 20px; border-radius: 15px; background: rgba(88, 166, 255, 0.05);
        border: 1px solid rgba(88, 166, 255, 0.2); text-align: center; margin-bottom: 25px;
    }
    .wishy-tag { font-size: 11px; color: #58a6ff; letter-spacing: 2.1px; font-weight: 800; margin-top: 10px; text-transform: uppercase; }
    .social-btn { background: white; color: black; padding: 8px; border-radius: 5px; text-align: center; margin-bottom: 8px; font-size: 14px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- ৩. এআই ইঞ্জিন (Human-like Thinking & Multi-Answer) ---
def get_advanced_response(query, res):
    with st.status("SkinAI is thinking...", expanded=False) as status:
        time.sleep(1.8)
        status.update(label="Analysis Done!", state="complete")
    
    q = query.lower()
    ans = []
    if any(w in q for w in ["keno", "why", "cause", "হলো"]):
        ans.append(f"🧬 **কারণ:** আপনার রিপোর্টে {res} পাওয়া গেছে। এটি মূলত অতিরিক্ত রোদ বা বংশগত কারণে ত্বকের কোষের পরিবর্তনের ফলে হয়।")
    if any(w in q for w in ["osud", "medicine", "solution", "ঔষধ"]):
        ans.append(f"⚠️ **সতর্কতা:** {res}-এর জন্য ডাক্তারের পরামর্শ ছাড়া কোনো ঔষধ ব্যবহার করবেন না।")
    
    return "\n\n---\n\n".join(ans) if ans else f"আমি আপনার ছবিতে **{res}** শনাক্ত করেছি। এর বাইরে আর কোনো প্রশ্ন আছে?"

# --- ৪. মডেল লোডিং ---
@st.cache_resource
def load_original_model():
    file_id = '1JpKXUXu_DsXK5-uq7fpgg5aDY7hBhq9h'
    model_path = 'skin_cancer_model.h5'
    if not os.path.exists(model_path):
        try: gdown.download(id=file_id, output=model_path, quiet=False, fuzzy=True)
        except: return None
    return tf.keras.models.load_model(model_path, compile=False)

model = load_original_model()
classes = ['Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis', 'Dermatofibroma', 'Melanoma', 'Nevus', 'Vascular lesions']

# --- ৫. সেশন ম্যানেজমেন্ট ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []
if 'last_res' not in st.session_state: st.session_state.last_res = "None"

# --- ৬. সাইডবার (Branding & Account) ---
with st.sidebar:
    st.markdown('<div class="brand-card">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3591/3591147.png", width=90)
    st.markdown('<p class="wishy-tag">Developed by Wishy</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    
    # লগইন সেকশন (ঐচ্ছিক - হিস্ট্রি সেভ করার জন্য)
    if not st.session_state.logged_in:
        with st.expander("👤 Login for History"):
            st.markdown('<div class="social-btn">🔵 Facebook Login</div>', unsafe_allow_html=True)
            st.markdown('<div class="social-btn">🔴 Gmail Login</div>', unsafe_allow_html=True)
            
            mode = st.radio("Mode", ["Login", "Sign Up"])
            u_email = st.text_input("Gmail")
            u_pass = st.text_input("Password", type="password")
            
            if mode == "Sign Up":
                if st.button("Create Account"):
                    if "@" in u_email and len(u_pass) > 3:
                        try:
                            c.execute('INSERT INTO users VALUES (?,?)', (u_email, make_hash(u_pass)))
                            conn.commit()
                            st.success("Done! Now Login.")
                        except: st.error("Exists!")
            else:
                if st.button("Enter"):
                    c.execute('SELECT password FROM users WHERE email=?', (u_email,))
                    data = c.fetchone()
                    if data and check_hash(u_pass, data[0]):
                        st.session_state.logged_in, st.session_state.user = True, u_email
                        c.execute('SELECT role, content FROM chat_history WHERE email=?', (u_email,))
                        st.session_state.messages = [{"role": r[0], "content": r[1]} for r in c.fetchall()]
                        st.rerun()
    else:
        st.info(f"Logged in: {st.session_state.user}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")
    with st.expander("⚙️ Settings"): st.write("v14.0 Stable")
    with st.expander("❓ Help"): st.write("Upload clear skin photo.")

# --- ৭. মেইন কন্টেন্ট (সরাসরি ওপেন) ---
st.title("🩺 SkinAI Assistant")

# ইমেজ আপলোডার এখন সরাসরি দেখা যাবে
file = st.file_uploader("আপনার ত্বকের ছবি আপলোড করুন...", type=["jpg", "png", "jpeg"])
if file:
    img = Image.open(file).convert('RGB')
    st.image(img, width=320)
    if model:
        img_res = img.resize((100, 75))
        x = np.asarray(img_res) / 255.0
        x = np.expand_dims(x, axis=0)
        pred = model.predict(x, verbose=0)
        st.session_state.last_res = classes[np.argmax(pred)]
        st.success(f"Detection: **{st.session_state.last_res}**")

st.markdown("---")

# চ্যাট ইন্টারফেস (সরাসরি ওপেন)
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    if st.session_state.logged_in:
        c.execute('INSERT INTO chat_history VALUES (?,?,?)', (st.session_state.user, "user", prompt))
        conn.commit()
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        reply = get_advanced_response(prompt, st.session_state.last_res)
        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        if st.session_state.logged_in:
            c.execute('INSERT INTO chat_history VALUES (?,?,?)', (st.session_state.user, "assistant", reply))
            conn.commit()
