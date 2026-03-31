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

# --- ১. ডাটাবেস সেটআপ ---
conn = sqlite3.connect('skinai_v2.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS history(username TEXT, result TEXT, confidence REAL, timestamp DATETIME)')
    conn.commit()

init_db()

# পাসওয়ার্ড হ্যাশ করার ফাংশন (সিকিউরিটির জন্য)
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# --- ২. পেজ কনফিগারেশন ও ডিজাইন ---
st.set_page_config(page_title="SkinAI Ultimate - Wishy", layout="wide")

st.markdown("""
<style>
    .stApp { background: radial-gradient(circle at top right, #1a1f25, #050505); color: #e0e0e0; }
    [data-testid="stSidebar"] { background: rgba(20, 25, 35, 0.9) !important; backdrop-filter: blur(15px); }
    .auth-card { padding: 40px; border-radius: 20px; background: #13171d; border: 1px solid #58a6ff33; text-align: center; max-width: 400px; margin: auto; }
</style>
""", unsafe_allow_html=True)

# --- ৩. লগইন এবং সাইন-আপ লজিক ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login_page():
    st.markdown("<h1 style='text-align: center; color: #58a6ff;'>🩺 SkinAI Login</h1>", unsafe_allow_html=True)
    choice = st.selectbox("Choose Action", ["Login", "Sign Up"])
    
    with st.container():
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        user = st.text_input("Username")
        passwd = st.text_input("Password", type='password')
        
        if choice == "Sign Up":
            if st.button("Create Account"):
                try:
                    c.execute('INSERT INTO users(username, password) VALUES (?,?)', (user, make_hashes(passwd)))
                    conn.commit()
                    st.success("Account Created! Please Login.")
                except:
                    st.error("Username already exists.")
        else:
            if st.button("Login"):
                c.execute('SELECT password FROM users WHERE username = ?', (user,))
                data = c.fetchone()
                if data and check_hashes(passwd, data[0]):
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.rerun()
                else:
                    st.error("Invalid Username/Password")
        st.markdown('</div>', unsafe_allow_html=True)

# --- ৪. মেইন অ্যাপ (লগইন সাকসেস হলে) ---
if not st.session_state.logged_in:
    login_page()
else:
    # আপনার আগের সেই সুন্দর সাইডবার ডিজাইন এখানে আসবে
    with st.sidebar:
        st.markdown(f"### 🛡️ Welcome, {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
        
        st.markdown("---")
        # হিস্ট্রি দেখানোর অপশন
        if st.checkbox("View My History"):
            st.subheader("📜 Past Reports")
            c.execute('SELECT result, confidence, timestamp FROM history WHERE username = ? ORDER BY timestamp DESC', (st.session_state.username,))
            user_history = c.fetchall()
            for h in user_history:
                st.write(f"🔍 {h[0]} ({h[1]}%)")
                st.caption(f"Date: {h[2]}")

    # মেইন ডিটেকশন লজিক (আপনার আগের কোডটি এখানে বসবে)
    st.markdown("<h1 style='color: #58a6ff;'>SkinAI Professional Analysis</h1>", unsafe_allow_html=True)
    
    # [এখানে আপনার আগের 'load_my_model' এবং 'get_natural_response' ফাংশন থাকবে]
    # [ইমেজ আপলোড এবং ডিটেকশন সেকশনে নিচের লাইনটি যোগ করতে হবে]
    
    # রেজাল্ট সেভ করার জন্য:
    # if result:
    #     import datetime
    #     c.execute('INSERT INTO history(username, result, confidence, timestamp) VALUES (?,?,?,?)', 
    #               (st.session_state.username, result, confidence, datetime.datetime.now()))
    #     conn.commit()
