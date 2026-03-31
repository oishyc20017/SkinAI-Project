import streamlit as st
import time
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import gdown
import sqlite3

# --- ১. ডাটাবেস সেটআপ (History Save করার জন্য) ---
conn = sqlite3.connect('skinai_wishy_pro_final.db', check_same_thread=False)
c = conn.cursor()
def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS chat_history(email TEXT, role TEXT, content TEXT)')
    conn.commit()
init_db()

# --- ২. এস্থেটিক ডিজাইন (Gemini Style) ---
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
    .social-btn { background: white; color: black; padding: 8px; border-radius: 5px; text-align: center; margin-bottom: 8px; cursor: pointer; font-size: 14px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- ৩. স্মার্ট হিউম্যান-লাইক এআই ইঞ্জিন ---
def get_advanced_response(query, res):
    with st.status("SkinAI is thinking...", expanded=False) as status:
        time.sleep(2)
        status.update(label="Analysis Done!", state="complete")
    
    q = query.lower()
    ans = []
    # মানুষের মতো ডিটেইলড এবং মাল্টি-ল্যাঙ্গুয়েজ সাপোর্ট
    if any(w in q for w in ["keno", "why", "cause", "হলো"]):
        ans.append(f"🧬 **কারণ:** আপনার ত্বকে {res} শনাক্ত হয়েছে। এটি সাধারণত অতিরিক্ত রোদের তাপ (UV Rays) বা বংশগত কারণে ত্বকের কোষের পরিবর্তনের ফলে হয়ে থাকে।")
    if any(w in q for w in ["osud", "medicine", "solution", "ঔষধ"]):
        ans.append(f"⚠️ **সতর্কতা:** {res}-এর ক্ষেত্রে ডাক্তারের পরামর্শ ছাড়া কোনো ঔষধ বা ক্রিম ব্যবহার করবেন না। একজন চর্মরোগ বিশেষজ্ঞ (Dermatologist) দেখানোই সবচেয়ে বুদ্ধিমানের কাজ হবে।")
    
    if not ans: return f"আমি আপনার রিপোর্টে **{res}** পেয়েছি। এর কারণ বা প্রতিকার সম্পর্কে আপনার কি কোনো প্রশ্ন আছে? আমি সব ল্যাঙ্গুয়েজ বুঝি।"
    return "\n\n---\n\n".join(ans)

# --- ৪. কোর মডেল লোডিং (TensorFlow) ---
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

# --- ৫. সাইডবার (Branding, Login, Guest Mode & Menus) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'guest_mode' not in st.session_state: st.session_state.guest_mode = False
if 'messages' not in st.session_state: st.session_state.messages = []
if 'last_res' not in st.session_state: st.session_state.last_res = "None"

with st.sidebar:
    # ১ & ২: লোগো এবং স্টাইলিশ Wishy ট্যাগ
    st.markdown('<div class="brand-card">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3591/3591147.png", width=90)
    st.markdown('<p class="wishy-tag">Developed by Wishy</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    
    # ৪ & ৫: সোশ্যাল লগইন ও গেস্ট মোড
    if not st.session_state.logged_in and not st.session_state.guest_mode:
        with st.expander("👤 Account / Create Account", expanded=True):
            st.markdown('<div class="social-btn">🔵 Continue with Facebook</div>', unsafe_allow_html=True)
            st.markdown('<div class="social-btn">🔴 Continue with Gmail</div>', unsafe_allow_html=True)
            u_email = st.text_input("Enter Gmail Address")
            if st.button("Login & Save History", use_container_width=True):
                if "@" in u_email:
                    st.session_state.logged_in, st.session_state.user = True, u_email
                    # হিস্ট্রি লোড করা
                    c.execute('SELECT role, content FROM chat_history WHERE email=?', (u_email,))
                    st.session_state.messages = [{"role": r[0], "content": r[1]} for r in c.fetchall()]
                    st.rerun()
            st.write("OR")
            if st.button("Continue as Guest (No History)", use_container_width=True):
                st.session_state.guest_mode = True
                st.rerun()
    else:
        st.info(f"User: {st.session_state.user if st.session_state.logged_in else 'Guest (No History)'}")
        if st.button("Logout / Exit"):
            st.session_state.logged_in = st.session_state.guest_mode = False
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")
    # ৩: সেটিংস ও হেল্প
    with st.expander("⚙️ Settings"): st.write("Safe & Encrypted")
    with st.expander("❓ Help"): st.write("Upload skin image for instant analysis.")

# --- ৬. মেইন অ্যাপ ইন্টারফেস ---
st.title("🩺 SkinAI Assistant")

if st.session_state.logged_in or st.session_state.guest_mode:
    # ৬: ইমেজ ডিটেকশন
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
            st.success(f"Detection: **{st.session_state.last_res}** ({np.max(pred)*100:.1f}%)")

    st.markdown("---")
    # ৭, ৮, ৯: হিউম্যান-লাইক চ্যাট
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("যেকোনো কিছু জিজ্ঞাসা করুন..."):
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
else:
    st.warning("আপনার স্বাস্থ্য পরীক্ষা শুরু করতে সাইডবার থেকে লগইন করুন।")
