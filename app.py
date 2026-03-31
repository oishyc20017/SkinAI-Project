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
def get_intelligent_response(query, res):
    # Thinking Animation
    with st.status("SkinAI is thinking...", expanded=False) as status:
        time.sleep(1.2)
        status.update(label="Analysis Done!", state="complete")
    
    q = query.lower()
    
    # ১. স্মার্ট ল্যাঙ্গুয়েজ ডিটেকশন (বাংলা অক্ষর বা বাংলিশ শব্দ চেক)
    is_bangla = any('\u0980' <= char <= '\u09FF' for char in query) or \
                any(word in q for word in ["ki", "keno", "ken", "hoyeche", "korbo", "bolun", "eta", "eita", "medicine", "osud"])
    
    ans = []
    if res == "None":
        return "দয়া করে আগে একটি ছবি আপলোড করুন।" if is_bangla else "Please upload a photo first."

    info = disease_info.get(res, {})

    # ২. মাল্টি-অ্যানসার লজিক (ইউজার যা যা জানতে চাবে সব পয়েন্ট আকারে আসবে)
    
    # বর্ণনা (Details)
    if any(w in q for w in ["ki", "what", "detail", "details", "বর্ণনা", "রোগ"]):
        header = "📘 **বিস্তারিত:** " if is_bangla else "📘 **Details:** "
        ans.append(f"{header}{info['bn' if is_bangla else 'en']}")

    # কারণ (Cause)
    if any(w in q for w in ["keno", "why", "cause", "হলো", "কারণ", "ken"]):
        if is_bangla:
            ans.append(f"🧬 **কারণ:** {res} মূলত সূর্যের অতিবেগুনি রশ্মি (UV) বা জীনগত পরিবর্তনের ফলে হয়।")
        else:
            ans.append(f"🧬 **Cause:** {res} is usually caused by prolonged UV radiation or genetic skin cell changes.")
            
    # সমাধান/ঔষধ (Solution/Medicine)
    if any(w in q for w in ["osud", "medicine", "solution", "ঔষধ", "korbo", "do", "treat"]):
        if is_bangla:
            ans.append(f"⚠️ **পরামর্শ:** বিশেষজ্ঞ ডাক্তারের অনুমতি ছাড়া কোনো ঔষধ বা ক্রিম ব্যবহার করবেন না।")
        else:
            ans.append(f"⚠️ **Suggestion:** Do not use any medication without consulting a dermatologist.")
    
    # যদি কোনো কি-ওয়ার্ড ম্যাচ না করে
    if not ans:
        if is_bangla:
            return f"আমি রিপোর্টে **{res}** শনাক্ত করেছি। আপনি কি এর বর্ণনা বা প্রতিকার সম্পর্কে জানতে চান?"
        else:
            return f"I detected **{res}** in your report. Would you like to know its details or treatment?"
    
    # একাধিক উত্তর থাকলে সেগুলো গ্যাপ দিয়ে সুন্দর করে সাজিয়ে দিবে
    return "\n\n---\n\n".join(ans)
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
        # ৫: সোশ্যাল বাটন
        st.markdown('<div class="social-btn">🔵 Continue with Facebook</div>', unsafe_allow_html=True)
        st.markdown('<div class="social-btn">🔴 Continue with Gmail</div>', unsafe_allow_html=True)
        
        # ৪: লগইন এবং ক্রিয়েট অ্যাকাউন্ট
        tab1, tab2 = st.tabs(["🔑 Login", "🆕 Create Account"])
        
        with tab1:
            l_email = st.text_input("Gmail", key="l_email")
            l_pass = st.text_input("Password", type="password", key="l_pass")
            if st.button("Login", use_container_width=True):
                c.execute('SELECT password FROM users WHERE email=?', (l_email,))
                data = c.fetchone()
                if data and check_hash(l_pass, data[0]):
                    st.session_state.logged_in, st.session_state.user = True, l_email
                    c.execute('SELECT role, content FROM chat_history WHERE email=?', (l_email,))
                    st.session_state.messages = [{"role": r[0], "content": r[1]} for r in c.fetchall()]
                    st.rerun()
                else: st.error("Wrong details.")
                
        with tab2:
            s_email = st.text_input("Gmail Address", key="s_email")
            s_pass = st.text_input("Set Password", type="password", key="s_pass")
            if st.button("Sign Up", use_container_width=True):
                if "@" in s_email and len(s_pass) > 3:
                    try:
                        c.execute('INSERT INTO users VALUES (?,?)', (s_email, make_hash(s_pass))); conn.commit()
                        st.success("Account Created! Please Login.")
                    except: st.error("Email already registered.")
                else: st.warning("Enter valid details.")
    else:
        st.info(f"User: {st.session_state.user}")
        if st.button("Logout"): st.session_state.logged_in = False; st.session_state.messages = []; st.rerun()

    st.markdown("---")
    with st.expander("⚙️ Settings"): st.write("v26.0 Stable")
    with st.expander("❓ Help"): st.write("Upload photo for skin diagnosis.")

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
