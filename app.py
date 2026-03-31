import streamlit as st
import time
import tensorflow as tf
from PIL import Image
import numpy as np
import os

# --- ১. এস্থেটিক ডিজাইন ---
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

# --- ২. স্মার্ট চ্যাট ইঞ্জিন (Thinking Logic) ---
def get_human_response(query, res):
    # এখানে আমরা থিঙ্কিং এমুলেট করব
    with st.spinner("SkinAI is thinking..."):
        time.sleep(1.5) # এটি একটি ছোট বিরতি দেবে যেন মনে হয় সে চিন্তা করছে
    
    q = query.lower()
    if any(word in q for word in ["keno", "why", "hoyeche"]):
        return f"🧬 আপনার রিপোর্টে **{res}** পাওয়া গেছে। এটি সাধারণত সূর্যের কড়া রোদ (UV Rays) বা অনেক সময় জিনগত কারণে হতে পারে। চিন্তার কিছু নেই, তবে সাবধানতা জরুরি।"
    
    if any(word in q for word in ["osud", "medicine", "solution"]):
        return f"⚠️ **{res}** এর ক্ষেত্রে কোনো ঔষধ বা ক্রিম সরাসরি ব্যবহার করা ঠিক হবে না। আমি আপনাকে একজন বিশেষজ্ঞ ডার্মাটোলজিস্ট দেখানোর পরামর্শ দিচ্ছি।"
    
    return f"আমি আপনার আপলোড করা ছবি থেকে **{res}** শনাক্ত করেছি। আপনি কি এর কারণ বা প্রতিকার সম্পর্কে জানতে চান?"

# --- ৩. সাইডবার (Branding & Login) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []
if 'last_result' not in st.session_state: st.session_state.last_result = "None"

with st.sidebar:
    st.markdown('<div class="brand-section">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3591/3591147.png", width=80)
    st.markdown('<p class="dev-tag">DEVELOPED BY WISHY</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    
    if not st.session_state.logged_in:
        gmail = st.text_input("Enter Gmail to Start", placeholder="yourname@gmail.com")
        if st.button("Continue", use_container_width=True):
            if "@gmail.com" in gmail:
                st.session_state.logged_in = True
                st.session_state.user = gmail
                st.rerun()
    else:
        st.success(f"User: {st.session_state.user}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- ৪. মেইন অ্যাপ ---
st.title("🩺 SkinAI Assistant")

if st.session_state.logged_in:
    file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file).convert('RGB')
        st.image(img, width=300)
        st.session_state.last_result = "Melanoma" # Placeholder (তোমার আসল মডেল এখানে বসবে)
        st.success(f"Detected: {st.session_state.last_result}")

    st.markdown("---")
    # চ্যাট ডিসপ্লে
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # ইনপুট বক্স
    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            # থিঙ্কিং লজিক কল করা
            response = get_human_response(prompt, st.session_state.last_result)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.info("Please enter your Gmail in the sidebar to begin.")
