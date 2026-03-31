import streamlit as st
import time
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import gdown
import sqlite3
import hashlib
from datetime import datetime

# --- ১. ডাটাবেস ও সিকিউরিটি ---
conn = sqlite3.connect('skinai_final.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, fullname TEXT, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS history(email TEXT, result TEXT, timestamp TEXT)')
    conn.commit()

init_db()

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(p, h): return h if make_hashes(p) == h else False

# --- ২. পেজ সেটআপ ও এস্থেটিক ডিজাইন ---
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e3e3e3; }
    [data-testid="stSidebar"] { background-color: #1e1f20 !important; border-right: 1px solid #30363d; }
    
    /* New Chat Button Style */
    .new-chat-btn {
        display: flex; align-items: center; justify-content: center;
        background: #282a2d; border: 1px solid #444746; border-radius: 50px;
        padding: 10px; cursor: pointer; transition: 0.3s; margin-bottom: 20px;
    }
    .new-chat-btn:hover { background: #333538; }
    
    /* Wishy Branding */
    .dev-credit { padding: 10px; border-radius: 10px; background: rgba(88, 166, 255, 0.05); border: 1px solid rgba(88, 166, 255, 0.2); text-align: center; margin-bottom: 15px; }
    .main-title { font-size: 32px; font-weight: 600; color: #c4c7c5; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- ৩. সেশন স্টেট ম্যানেজমেন্ট ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []

def reset_chat():
    st.session_state.messages = []
    st.rerun()

# --- ৪. সাইডবার (Gemini Layout) ---
with st.sidebar:
    # ১. ডেভলপার ক্রেডিট
    st.markdown("""
        <div class="dev-credit">
            <p style="margin:0; font-size:10px; color:#8b949e;">CHIEF ARCHITECT</p>
            <h4 style="margin:0; color:#58a6ff;">WISHY CHAKMA</h4>
        </div>
    """, unsafe_allow_html=True)

    # ২. নিউ চ্যাট বাটন
    if st.button("➕ New Chat", use_container_width=True):
        reset_chat()

    st.markdown("---")

    # ৩. চ্যাট হিস্ট্রি (লগইন থাকলে)
    st.markdown("### 🕒 Recent")
    if st.session_state.logged_in:
        c.execute('SELECT result, timestamp FROM history WHERE email = ? ORDER BY timestamp DESC LIMIT 5', (st.session_state.email,))
        rows = c.fetchall()
        if rows:
            for row in rows:
                st.caption(f"🔍 {row[0]} ({row[1]})")
        else:
            st.caption("No history yet.")
    else:
        st.info("Log in to see history.")

    # ৪. সাইডবার ফুটার (Settings, Help, Login)
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.expander("❓ Help"):
        st.write("• Upload clear skin images.")
        st.write("• Describe symptoms in chat.")
    
    with st.expander("⚙️ Settings"):
        st.write("Theme: Gemini Dark")
        st.write("Data Privacy: Encrypted")

    if not st.session_state.logged_in:
        with st.expander("👤 Log In"):
            email = st.text_input("Gmail")
            p = st.text_input("Password", type='password')
            if st.button("Sign In"):
                c.execute('SELECT fullname, password FROM users WHERE email = ?', (email,))
                data = c.fetchone()
                if data and check_hashes(p, data[1]):
                    st.session_state.logged_in = True
                    st.session_state.email = email
                    st.session_state.fullname = data[0]
                    st.rerun()
            st.caption("Don't have an account? Use Sign Up.")
        
        with st.expander("📝 Sign Up"):
            fname = st.text_input("Name")
            n_email = st.text_input("Enter Gmail")
            n_p = st.text_input("New Password", type='password')
            if st.button("Create Account"):
                try:
                    c.execute('INSERT INTO users VALUES (?,?,?)', (n_email, fname, make_hashes(n_p)))
                    conn.commit()
                    st.success("Welcome! Now Log In.")
                except: st.error("Email exists.")
    else:
        st.markdown(f"**Member:** {st.session_state.fullname}")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- ৫. মেইন কন্টেন্ট ---
st.markdown('<div class="main-title">SkinAI Assistant</div>', unsafe_allow_html=True)

# ইমেজ আপলোড সেকশন (পাবলিক)
file = st.file_uploader("Upload an image to analyze condition", type=["jpg", "png", "jpeg"])

if file:
    img = Image.open(file).convert('RGB')
    st.image(img, width=350, caption="Uploaded Image")
    st.success("Analysis Complete: [Dummy Result - Nevus 98.4%]")
    
    if st.session_state.logged_in:
        if st.button("💾 Save to History"):
            ts = datetime.now().strftime("%d %b")
            c.execute('INSERT INTO history VALUES (?,?,?)', (st.session_state.email, "Nevus", ts))
            conn.commit()
            st.toast("Saved to your profile!")

# চ্যাটবট ইন্টারফেস
st.markdown("---")
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Ask me anything about skin health..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        # মাল্টি-অ্যানসার লজিক এখানে কল হবে
        response = "I'm analyzing your request... This is where the smart response goes."
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
