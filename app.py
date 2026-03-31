import streamlit as st
import time
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import gdown
import sqlite3
import hashlib

# --- ১. ডাটাবেস ও সিকিউরিটি (আপনার জিমেইল লগইন সিস্টেম) ---
# এটি ডিলিট করা হয়নি, শুধু নতুন ডাটাবেস কানেকশন করা হয়েছে
conn = sqlite3.connect('skinai_complete_v10.db', check_same_thread=False)
c = conn.cursor()
def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, fullname TEXT)')
    conn.commit()
init_db()

# --- ২. প্রিমিয়াম ডিজাইন ও ব্র্যান্ডিং (Logo & Wishy Tag) ---
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e3e3e3; }
    [data-testid="stSidebar"] { background-color: #1e1f20 !important; border-right: 1px solid #30363d; }
    
    /* Wishy's Brand Card */
    .brand-section {
        padding: 20px; border-radius: 15px; 
        background: rgba(88, 166, 255, 0.05);
        border: 1px solid rgba(88, 166, 255, 0.2); 
        text-align: center; margin-bottom: 25px;
    }
    .dev-tag { 
        font-size: 11px; color: #58a6ff; letter-spacing: 2px; 
        font-weight: bold; margin-top: 10px; text-transform: uppercase; 
    }
</style>
""", unsafe_allow_html=True)

# --- ৩. স্মার্ট হিউম্যান-লাইক চ্যাট ইঞ্জিন (Thinking Logic) ---
def get_intelligent_response(query, condition):
    # Thinking Animation (আপনি যা চেয়েছিলেন)
    with st.spinner("SkinAI is thinking..."):
        time.sleep(2) # ২ সেকেন্ড চিন্তা করার ভাব করা
    
    q = query.lower()
    responses = {
        'cause': f"🧬 **বিশ্লেষণ:** আপনার রিপোর্টে {condition} দেখা যাচ্ছে। এটি মূলত দীর্ঘসময় রোদে থাকা (UV exposure) অথবা মেলানোসাইট কোষের পরিবর্তনের কারণে হতে পারে।",
        'medicine': f"⚠️ **সতর্কতা:** {condition} এর জন্য সরাসরি কোনো ঔষধ ব্যবহার করা ঝুঁকিপূর্ণ। আমি আপনাকে একজন বিশেষজ্ঞ ডার্মাটোলজিস্টের পরামর্শ নিতে অনুরোধ করছি।",
        'general': f"আমি আপনার আপলোড করা ছবি থেকে {condition} শনাক্ত করেছি। আপনি কি এর প্রতিকার বা কারণ জানতে চান?"
    }

    # মাল্টি-অ্যানসার লজিক (সব উত্তর একবারে দিবে)
    output = []
    if any(word in q for word in ["keno", "why", "cause", "hoyeche"]):
        output.append(responses['cause'])
    if any(word in q for word in ["osud", "medicine", "treatment", "solution"]):
        output.append(responses['medicine'])
    
    if not output: return responses['general']
    return "\n\n".join(output)

# --- ৪. আপনার অরিজিনাল মডেল লোডিং (Cache সহ) ---
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

# --- ৫. সাইডবার (New Logo, Direct Login & Options) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []
if 'last_result' not in st.session_state: st.session_state.last_result = "None"

with st.sidebar:
    # ব্র্যান্ডিং সেকশন
    st.markdown('<div class="brand-section">', unsafe_allow_html=True)
    # ১০০% গ্যারান্টিড প্রিমিয়াম লোগো
    st.image("https://cdn-icons-png.flaticon.com/512/3591/3591147.png", width=90)
    st.markdown('<p class="dev-tag">DEVELOPED BY WISHY</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    
    # ChatGPT Style Simple Login (পাসওয়ার্ড ছাড়াই)
    if not st.session_state.logged_in:
        st.write("### Welcome Back")
        user_gmail = st.text_input("Enter Gmail to Login", placeholder="example@gmail.com")
        if st.button("Continue with Gmail", use_container_width=True):
            if "@gmail.com" in user_gmail:
                st.session_state.logged_in = True
                st.session_state.user = user_gmail
                st.rerun()
            else: st.error("Please enter a valid Gmail")
    else:
        st.info(f"Logged in: {st.session_state.user}")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("---")
    with st.expander("❓ Help"): st.write("ক্লিয়ার ছবি আপলোড করে এআই চ্যাটবটকে প্রশ্ন করুন।")
    with st.expander("⚙️ Settings"): st.write("Build: v10.0.1 Stable")

# --- ৬. মেইন অ্যাপ ইন্টারফেস ---
st.title("🩺 SkinAI Assistant")

if st.session_state.logged_in:
    # ইমেজ আপলোডার
    file = st.file_uploader("আপনার ত্বকের ছবি এখানে আপলোড করুন...", type=["jpg", "png", "jpeg"])
    
    if file:
        img = Image.open(file).convert('RGB')
        st.image(img, width=350)
        
        # ডিটেকশন প্রসেস (আসল মডেল দিয়ে)
        if model:
            img_res = img.resize((100, 75))
            x = np.asarray(img_res) / 255.0
            x = np.expand_dims(x, axis=0)
            pred = model.predict(x, verbose=0)
            st.session_state.last_result = classes[np.argmax(pred)]
            conf = np.max(pred) * 100
            st.success(f"রিপোর্ট: **{st.session_state.last_result}** ({conf:.1f}%)")
        else:
            st.error("Model not loaded yet!")

    st.markdown("---")
    # চ্যাট হিস্ট্রি
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # স্মার্ট চ্যাট ইনপুট (বক্স এখন ক্লিন)
    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            # হিউম্যান-লাইক রেসপন্স এবং থিঙ্কিং লজিক
            reply = get_intelligent_response(prompt, st.session_state.last_result)
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
else:
    st.warning("আপনার স্বাস্থ্য পরীক্ষা শুরু করতে সাইডবার থেকে জিমেইল দিয়ে লগইন করুন।")
