import streamlit as st
import time
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import gdown
import sqlite3
import hashlib

# --- ১. ডাটাবেস ও সিকিউরিটি (History & Password) ---
conn = sqlite3.connect('skinai_wishy_ultimate_v20.db', check_same_thread=False)
c = conn.cursor()
def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS chat_history(email TEXT, role TEXT, content TEXT)')
    conn.commit()
init_db()

def make_hash(p): return hashlib.sha256(str.encode(p)).hexdigest()
def check_hash(p, h): return h if make_hash(p) == h else False

# --- ২. এস্থেটিক ডিজাইন (Logo & Developed by Wishy) ---
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e3e3e3; }
    [data-testid="stSidebar"] { background-color: #1e1f20 !important; border-right: 1px solid #30363d; }
    .brand-card {
        padding: 20px; border-radius: 15px; background: rgba(88, 166, 255, 0.05);
        border: 1px solid rgba(88, 166, 255, 0.2); text-align: center; margin-bottom: 25px;
    }
    .wishy-tag { font-size: 11px; color: #58a6ff; letter-spacing: 2px; font-weight: 800; margin-top: 10px; text-transform: uppercase; }
    .social-btn { background: white; color: black; padding: 8px; border-radius: 5px; text-align: center; margin-bottom: 8px; font-weight: bold; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# --- ৩. রোগের নলেজ বেস (৭টি রোগ) ---
disease_info = {
    'Actinic keratoses': {'bn': "এটি খসখসে রোদে পোড়া দাগ। এটি ক্যান্সারের পূর্বাবস্থা হতে পারে।", 'en': "Rough, scaly patches caused by sun exposure. Can be precancerous."},
    'Basal cell carcinoma': {'bn': "এটি সাধারণ স্কিন ক্যান্সার। এটি ধীরে বাড়ে কিন্তু চিকিৎসা প্রয়োজন।", 'en': "A common skin cancer that grows slowly but needs medical care."},
    'Benign keratosis': {'bn': "এটি ক্ষতিকারক নয়। বয়সের কারণে ত্বকে এমন দাগ হতে পারে।", 'en': "Non-cancerous skin growth often related to aging."},
    'Dermatofibroma': {'bn': "এটি ত্বকের নিচে শক্ত ছোট পিণ্ড। সাধারণত ক্ষতিকর নয়।", 'en': "Small, firm skin growths that are usually harmless."},
    'Melanoma': {'bn': "এটি মারাত্মক স্কিন ক্যান্সার। দ্রুত ডার্মাটোলজিস্ট দেখান।", 'en': "The most serious skin cancer. Consult a doctor immediately."},
    'Nevus': {'bn': "এটি সাধারণ তিল। রঙ বা আকার বদলালে পরীক্ষা করুন।", 'en': "A common mole. Check if it changes color or shape."},
    'Vascular lesions': {'bn': "রক্তনালীর অস্বাভাবিকতায় লাল দাগ। এটি সাধারণত ক্ষতিকর নয়।", 'en': "Red marks from abnormal blood vessels, usually harmless."}
}

# --- ৪. স্মার্ট এআই ইঞ্জিন (Language Logic Fixed) ---
def get_advanced_response(query, res):
    with st.status("SkinAI is thinking...", expanded=False) as status:
        time.sleep(1.5)
        status.update(label="Analysis Complete!", state="complete")
    
    q = query.lower()
    # স্মার্ট ল্যাঙ্গুয়েজ ডিটেকশন
    is_bangla = any(char > '\u0980' and char < '\u09FF' for char in query)
    ans = []

    if res == "None":
        return "দয়া করে আগে একটি ছবি আপলোড করুন।" if is_bangla else "Please upload a photo first."

    # রোগের বর্ণনা
    if any(w in q for w in ["ki", "what", "detail", "বর্ণনা", "রোগ"]):
        info = disease_info.get(res, {})
        ans.append(f"📘 **Details:** {info['bn' if is_bangla else 'en']}")

    # কারণ
    if any(w in q for w in ["keno", "why", "cause", "হলো", "কারণ"]):
        if is_bangla: ans.append(f"🧬 **কারণ:** {res} মূলত অতিরিক্ত রোদ বা জীনগত পরিবর্তনের ফলে হয়।")
        else: ans.append(f"🧬 **Cause:** {res} is usually caused by UV rays or genetic changes.")
            
    # ঔষধ
    if any(w in q for w in ["osud", "medicine", "solution", "ঔষধ"]):
        if is_bangla: ans.append(f"⚠️ **সতর্কতা:** ডাক্তারের পরামর্শ ছাড়া কোনো ঔষধ ব্যবহার করবেন না।")
        else: ans.append(f"⚠️ **Caution:** Do not use any medicine without a doctor's advice.")
    
    if not ans:
        return f"আমি রিপোর্টে **{res}** পেয়েছি। বিস্তারিত জানতে চান?" if is_bangla else f"I found **{res}**. Want to know more?"
    return "\n\n---\n\n".join(ans)

# --- ৫. মডেল লোডিং ও সাইডবার ---
@st.cache_resource
def load_model():
    path = 'skin_cancer_model.h5'
    if not os.path.exists(path): gdown.download(id='1JpKXUXu_DsXK5-uq7fpgg5aDY7hBhq9h', output=path, quiet=False)
    return tf.keras.models.load_model(path, compile=False)

model = load_model()
classes = list(disease_info.keys())

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []
if 'last_res' not in st.session_state: st.session_state.last_res = "None"

with st.sidebar:
    st.markdown('<div class="brand-card">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3591/3591147.png", width=90)
    st.markdown('<p class="wishy-tag">Developed by Wishy</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    if not st.session_state.logged_in:
        with st.expander("👤 Login for History", expanded=True):
            st.markdown('<div class="social-btn">🔵Continue with Facebook</div><div class="social-btn">🔴Continue with Gmail</div>', unsafe_allow_html=True)
            mode = st.radio("Mode", ["Login", "Sign Up"])
            u_email = st.text_input("Email")
            u_pass = st.text_input("Password", type="password")
            if st.button("Enter"):
                if mode == "Sign Up":
                    c.execute('INSERT INTO users VALUES (?,?)', (u_email, make_hash(u_pass))); conn.commit()
                    st.success("Account Created!")
                else:
                    c.execute('SELECT password FROM users WHERE email=?', (u_email,))
                    data = c.fetchone()
                    if data and check_hash(u_pass, data[0]):
                        st.session_state.logged_in, st.session_state.user = True, u_email
                        c.execute('SELECT role, content FROM chat_history WHERE email=?', (u_email,))
                        st.session_state.messages = [{"role": r[0], "content": r[1]} for r in c.fetchall()]
                        st.rerun()
    else:
        st.info(f"User: {st.session_state.user}")
        if st.button("Logout"): st.session_state.logged_in = False; st.session_state.messages = []; st.rerun()

    st.markdown("---")
    with st.expander("⚙️ Settings"): st.write("v20.0 Stable")
    with st.expander("❓ Help"): st.write("Upload clear skin photo.")

# --- ৬. মেইন কন্টেন্ট ---
st.title("🩺 SkinAI Assistant")
file = st.file_uploader("Upload Skin Photo", type=["jpg", "png", "jpeg"])
if file:
    img = Image.open(file).convert('RGB')
    st.image(img, width=320)
    if model:
        img_res = img.resize((100, 75))
        x = np.asarray(img_res) / 255.0; x = np.expand_dims(x, axis=0)
        pred = model.predict(x, verbose=0)
        st.session_state.last_res = classes[np.argmax(pred)]
        st.success(f"Detection: **{st.session_state.last_res}**")

st.markdown("---")
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    if st.session_state.logged_in:
        c.execute('INSERT INTO chat_history VALUES (?,?,?)', (st.session_state.user, "user", prompt)); conn.commit()
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        reply = get_advanced_response(prompt, st.session_state.last_res)
        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        if st.session_state.logged_in:
            c.execute('INSERT INTO chat_history VALUES (?,?,?)', (st.session_state.user, "assistant", reply)); conn.commit()
