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
conn = sqlite3.connect('skinai_wishy_v26.db', check_same_thread=False)
c = conn.cursor()
def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS chat_history(email TEXT, role TEXT, content TEXT)')
    conn.commit()
init_db()

def make_hash(p): return hashlib.sha256(str.encode(p)).hexdigest()
def check_hash(p, h): return h if make_hash(p) == h else False

# --- ২. ডিজাইন (Brand & Logo) ---
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
    .social-btn { background: white; color: black; padding: 8px; border-radius: 5px; text-align: center; margin-bottom: 8px; font-weight: bold; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# --- ৩. রোগের নলেজ বেস ---
disease_info = {
    'Actinic keratoses': {'bn': "এটি খসখসে রোদে পোড়া দাগ। এটি ক্যান্সার হওয়ার আগের ধাপ হতে পারে।", 'en': "Rough, scaly patches caused by sun exposure. Can be precancerous."},
    'Basal cell carcinoma': {'bn': "এটি সাধারণ স্কিন ক্যান্সার। এটি ধীরে বাড়ে কিন্তু চিকিৎসা জরুরি।", 'en': "A common skin cancer that grows slowly but needs treatment."},
    'Benign keratosis': {'bn': "এটি ক্ষতিকারক নয়। বয়সের কারণে ত্বকে এমন দাগ হতে পারে।", 'en': "Non-cancerous skin growth often related to aging."},
    'Dermatofibroma': {'bn': "এটি ত্বকের নিচে শক্ত ছোট পিণ্ড। সাধারণত ক্ষতিকর নয়।", 'en': "Small, firm skin growths that are usually harmless."},
    'Melanoma': {'bn': "এটি মারাত্মক স্কিন ক্যান্সার। দ্রুত বিশেষজ্ঞ ডাক্তার দেখান।", 'en': "The most serious skin cancer. Consult a specialist immediately."},
    'Nevus': {'bn': "এটি সাধারণ তিল। আকার বা রঙ বদলালে পরীক্ষা করুন।", 'en': "A common mole. Check if it changes shape or color."},
    'Vascular lesions': {'bn': "রক্তনালীর অস্বাভাবিকতায় লাল দাগ। সাধারণত বিপজ্জনক নয়।", 'en': "Red marks from abnormal blood vessels, usually harmless."}
}

# --- ৪. স্মার্ট এআই ইঞ্জিন ---
# --- ৩. স্মার্ট মাল্টি-ল্যাঙ্গুয়েজ ও মাল্টি-অ্যানসার ইঞ্জিন ---
# --- স্মার্ট মাল্টি-অ্যানসার ও মাল্টি-ল্যাঙ্গুয়েজ ইঞ্জিন (উইশ-এর জন্য ফাইনাল ফিক্স) ---
def get_intelligent_response(query, res):
    # এআই থিংকিং অ্যানিমেশন
    with st.status("SkinAI is thinking...", expanded=False) as status:
        time.sleep(1.2)
        status.update(label="Analysis Done!", state="complete")
    
    q = query.lower()
    
    # ১. পিউর ল্যাঙ্গুয়েজ ডিটেকশন (বাংলা অক্ষর বা বাংলিশ কমন শব্দ চেক)
    is_bangla = any('\u0980' <= char <= '\u09FF' for char in query) or \
                any(word in q for word in ["ki", "keno", "ken", "hoyeche", "korbo", "eta", "eita", "osud"])
    
    ans = []
    if res == "None":
        return "দয়া করে আগে একটি ছবি আপলোড করুন।" if is_bangla else "Please upload a photo first."

    info = disease_info.get(res, {})

    # ২. মাল্টি-কোয়েশ্চেন লজিক (প্রতিটি পয়েন্ট আলাদাভাবে চেক হবে)
    
    # বর্ণনা চেক
    if any(w in q for w in ["ki", "what", "detail", "details", "বর্ণনা", "রোগ"]):
        header = "📘 **বিস্তারিত:** " if is_bangla else "📘 **Details:** "
        ans.append(f"{header}{info['bn' if is_bangla else 'en']}")

    # কারণ চেক
    if any(w in q for w in ["keno", "why", "cause", "হলো", "কারণ", "ken"]):
        if is_bangla:
            ans.append(f"🧬 **কারণ:** {res} মূলত সূর্যের অতিবেগুনি রশ্মি (UV) বা জীনগত পরিবর্তনের ফলে হয়।")
        else:
            ans.append(f"🧬 **Cause:** {res} is usually caused by prolonged UV radiation or genetic skin cell changes.")
            
    # সমাধান/ঔষধ/ডাক্তার চেক
    if any(w in q for w in ["osud", "medicine", "solution", "ঔষধ", "korbo", "do", "treat", "doctor", "recommend"]):
        if is_bangla:
            ans.append(f"⚠️ **পরামর্শ:** বিশেষজ্ঞ ডাক্তারের অনুমতি ছাড়া কোনো ঔষধ বা ক্রিম ব্যবহার করবেন না।")
        else:
            ans.append(f"⚠️ **Suggestion:** Do not use any medication or cream without consulting a dermatologist.")
    
    # ৩. ফাইনাল রেজাল্ট সাজানো
    if ans:
        # একাধিক উত্তর থাকলে সেগুলো আলাদা লাইনে সুন্দর করে দেখাবে
        return "\n\n---\n\n".join(ans)
    else:
        # যদি কোনো কি-ওয়ার্ডই না মেলে
        if is_bangla:
            return f"আমি রিপোর্টে **{res}** শনাক্ত করেছি। বিস্তারিত, কারণ বা ঔষধ সম্পর্কে জানতে প্রশ্ন করুন।"
        else:
            return f"I detected **{res}**. Ask me about its details, cause, or treatment."
# --- ৫. মডেল লোডিং ---
@st.cache_resource
def load_skin_model():
    path = 'skin_cancer_model.h5'
    if not os.path.exists(path): gdown.download(id='1JpKXUXu_DsXK5-uq7fpgg5aDY7hBhq9h', output=path, quiet=False)
    return tf.keras.models.load_model(path, compile=False)

model = load_skin_model()
classes = list(disease_info.keys())

# --- ৬. সাইডবার (Account & Create Account Clearly) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []
if 'last_res' not in st.session_state: st.session_state.last_res = "None"
    # --- সাইডবার (সোশ্যাল বাটন ও লগইন আপডেট) ---
# সোশ্যাল বাটন সেকশন (শুধু এই অংশটুকু রিপ্লেস করো)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔵 Facebook", use_container_width=True):
                st.info("Social login will be available in the next pro version!")
        with col2:
            if st.button("🔴 Gmail", use_container_width=True):
                st.info("Direct Google Auth is coming soon!")
    if not st.session_state.logged_in:
        # সোশ্যাল বাটনগুলোতে এখন ক্লিকেবল লিংক বা অ্যাকশন যোগ করা হয়েছে
        # এখানে তোমার নিজের গুগল বা ফেসবুক লিংক বসাতে পারো
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔵 Facebook", use_container_width=True):
                st.markdown('<meta http-equiv="refresh" content="0;URL=\'https://www.facebook.com/login\'">', unsafe_allow_html=True)
        with col2:
            if st.button("🔴 Gmail", use_container_width=True):
                st.markdown('<meta http-equiv="refresh" content="0;URL=\'https://accounts.google.com\'">', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # লগইন এবং ক্রিয়েট অ্যাকাউন্ট ট্যাব
        tab1, tab2 = st.tabs(["🔑 Login", "🆕 Create Account"])
        
        with tab1:
            l_email = st.text_input("Gmail", key="login_email")
            l_pass = st.text_input("Password", type="password", key="login_pass")
            if st.button("Enter Login", use_container_width=True):
                c.execute('SELECT password FROM users WHERE email=?', (l_email,))
                data = c.fetchone()
                if data and check_hash(l_pass, data[0]):
                    st.session_state.logged_in, st.session_state.user = True, l_email
                    c.execute('SELECT role, content FROM chat_history WHERE email=?', (l_email,))
                    st.session_state.messages = [{"role": r[0], "content": r[1]} for r in c.fetchall()]
                    st.rerun()
                else:
                    st.error("Invalid Email or Password")

        with tab2:
            s_email = st.text_input("New Gmail", key="signup_email")
            s_pass = st.text_input("New Password", type="password", key="signup_pass")
            if st.button("Confirm Sign Up", use_container_width=True):
                if "@" in s_email and len(s_pass) >= 4:
                    try:
                        c.execute('INSERT INTO users VALUES (?,?)', (s_email, make_hash(s_pass)))
                        conn.commit()
                        st.success("Account Created! Now Login.")
                    except:
                        st.error("User already exists!")
                else:
                    st.warning("Please enter a valid Gmail & 4+ digit password.")

# --- ৭. মেইন চ্যাট ইন্টারফেস ---
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
        st.success(f"Detection Result: **{st.session_state.last_res}**")

st.markdown("---")
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("যেকোনো কিছু জিজ্ঞাসা করুন / Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    if st.session_state.logged_in:
        c.execute('INSERT INTO chat_history VALUES (?,?,?)', (st.session_state.user, "user", prompt)); conn.commit()
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        reply = get_intelligent_response(prompt, st.session_state.last_res)
        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        if st.session_state.logged_in:
            c.execute('INSERT INTO chat_history VALUES (?,?,?)', (st.session_state.user, "assistant", reply)); conn.commit()
