import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import sqlite3

# --- ১. ডাটাবেস ও ইউজার সিস্টেম ---
conn = sqlite3.connect('skinai_wishy_v9.db', check_same_thread=False)
c = conn.cursor()
def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY)')
    conn.commit()
init_db()

# --- ২. এস্থেটিক ডিজাইন (Gemini Style) ---
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e3e3e3; }
    [data-testid="stSidebar"] { background-color: #1e1f20 !important; border-right: 1px solid #30363d; }
    .brand-section {
        padding: 15px; border-radius: 12px; background: rgba(88, 166, 255, 0.05);
        border: 1px solid rgba(88, 166, 255, 0.2); text-align: center; margin-bottom: 20px;
    }
    .dev-tag { font-size: 11px; color: #58a6ff; letter-spacing: 1.5px; font-weight: bold; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- ৩. স্মার্ট চ্যাট লজিক (Memory + Multi-Answer) ---
def get_ai_response(query, res):
    q = query.lower()
    # যদি আগে একবার ডিটেকশন হয়ে থাকে, তবে চ্যাটবট সেটা মনে রেখে উত্তর দিবে
    responses = {
        'keno': "🧬 **কারণ:** এটি মূলত রোদের অতিবেগুনি রশ্মি (UV Rays) বা বংশগত কারণে হতে পারে।",
        'osud': "⚠️ **পরামর্শ:** ডাক্তারের পরামর্শ ছাড়া কোনো ক্রিম বা ঔষধ ব্যবহার করবেন না। একজন ডার্মাটোলজিস্ট দেখান।",
        'doctor': "👨‍⚕️ আপনার নিকটস্থ চর্মরোগ বিশেষজ্ঞের সাথে যোগাযোগ করা উচিত।",
        'hi': "হ্যালো! আমি আপনার ত্বকের রিপোর্ট বিশ্লেষণ করতে পারি। আপনার প্রশ্নটি করুন।"
    }
    
    output = []
    if any(word in q for word in ["keno", "why", "cause", "hoyeche"]): output.append(responses['keno'])
    if any(word in q for word in ["osud", "medicine", "treatment", "solution"]): output.append(responses['osud'])
    
    if not output:
        return f"আমি আপনার রিপোর্টে **{res}** পেয়েছি। আপনি কি এর কারণ বা ঔষধ সম্পর্কে জানতে চান?"
    
    return "\n\n".join(output)

# --- ৪. সাইডবার (Clean Logo & Login) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []
if 'last_result' not in st.session_state: st.session_state.last_result = "No Image Uploaded"

with st.sidebar:
    st.markdown('<div class="brand-section">', unsafe_allow_html=True)
    # ১০০% কাজ করবে এমন লোগো লিঙ্ক
    st.image("https://cdn-icons-png.flaticon.com/512/3591/3591147.png", width=80)
    st.markdown('<p class="dev-tag">DEVELOPED BY WISHY</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    
    if not st.session_state.logged_in:
        st.write("### Welcome")
        gmail = st.text_input("Enter Gmail", placeholder="example@gmail.com")
        if st.button("Continue with Gmail", use_container_width=True):
            if "@gmail.com" in gmail:
                st.session_state.logged_in = True
                st.session_state.user = gmail
                st.rerun()
            else: st.error("Invalid Gmail")
    else:
        st.info(f"User: {st.session_state.user}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("---")
    with st.expander("❓ Help"): st.write("Upload a clear skin image for analysis.")
    with st.expander("⚙️ Settings"): st.write("v9.0.1 Stable")

# --- ৫. মেইন কন্টেন্ট ---
st.title("🩺 SkinAI Assistant")

if st.session_state.logged_in:
    file = st.file_uploader("Upload Skin Image", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file).convert('RGB')
        st.image(img, width=300)
        # এখানে তোমার মডেল প্রেডিকশন লজিক বসবে
        st.session_state.last_result = "Melanoma" # Placeholder
        st.success(f"Detection: {st.session_state.last_result}")

    st.markdown("---")
    # চ্যাট হিস্ট্রি ডিসপ্লে
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # ইনপুট বক্স (এখান থেকে ডিফল্ট লেখা সরিয়ে দিয়েছি)
    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            response = get_ai_response(prompt, st.session_state.last_result)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.warning("Please login with Gmail to start diagnosis.")
