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
conn = sqlite3.connect('skinai_wishy_v30.db', check_same_thread=False)
c = conn.cursor()
def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS chat_history(email TEXT, role TEXT, content TEXT)')
    conn.commit()
init_db()

def make_hash(p): return hashlib.sha256(str.encode(p)).hexdigest()
def check_hash(p, h): return h if make_hash(p) == h else False

# --- ২. ডিজাইন ও এস্থেটিকস ---
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e3e3e3; }
    [data-testid="stSidebar"] { background-color: #1e1f20 !important; border-right: 1px solid #30363d; }
    .brand-card { padding: 20px; border-radius: 15px; background: rgba(88, 166, 255, 0.05); border: 1px solid rgba(88, 166, 255, 0.2); text-align: center; margin-bottom: 25px; }
    .wishy-tag { font-size: 11px; color: #58a6ff; letter-spacing: 2px; font-weight: 800; margin-top: 10px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# --- ৩. রোগের ডাটাবেস ---
disease_info = {
    'Actinic keratoses': {'bn': "এটি খসখসে রোদে পোড়া দাগ। এটি ক্যান্সার হওয়ার আগের ধাপ হতে পারে।", 'en': "Rough, scaly patches caused by sun exposure. It can be precancerous."},
    'Basal cell carcinoma': {'bn': "এটি সাধারণ স্কিন ক্যান্সার। এটি ধীরে বাড়ে কিন্তু চিকিৎসা জরুরি।", 'en': "A common skin cancer that grows slowly but needs medical treatment."},
    'Benign keratosis': {'bn': "এটি ক্ষতিকারক নয়। বয়সের কারণে ত্বকে এমন দাগ হতে পারে।", 'en': "Non-cancerous skin growth often related to aging."},
    'Dermatofibroma': {'bn': "এটি ত্বকের নিচে শক্ত ছোট পিণ্ড। সাধারণত ক্ষতিকর নয়।", 'en': "Small, firm skin growths that are usually harmless."},
    'Melanoma': {'bn': "এটি মারাত্মক স্কিন ক্যান্সার। দ্রুত বিশেষজ্ঞ ডাক্তার দেখান।", 'en': "The most serious type of skin cancer. Consult a specialist immediately."},
    'Nevus': {'bn': "এটি সাধারণ তিল। আকার বা রঙ বদলালে পরীক্ষা করুন।", 'en': "A common mole. Check if it changes shape or color rapidly."},
    'Vascular lesions': {'bn': "রক্তনালীর অস্বাভাবিকতায় লাল দাগ। সাধারণত বিপজ্জনক নয়।", 'en': "Red marks from abnormal blood vessels, usually harmless."}
}

# --- ৪. স্মার্ট রিপ্লাই ইঞ্জিন (Updated for Smart Answers) ---
def get_intelligent_response(query, res):
    with st.status("SkinAI is analyzing your question...", expanded=False) as status:
        time.sleep(1.0)
        status.update(label="Analysis Done!", state="complete")
    
    q = query.lower()
    is_bangla = any('\u0980' <= char <= '\u09FF' for char in query) or \
                any(word in q.split() for word in ["ki", "keno", "ken", "eta", "osud", "doctor", "val", "valo"])
    
    if res == "None":
        return "দয়া করে আগে একটি ছবি আপলোড করুন।" if is_bangla else "Please upload a photo first to get context."

    info = disease_info.get(res, {})
    ans = []

    # ১. বিস্তারিত জানতে চাইলে
    if any(w in q for w in ["ki", "what", "detail", "details", "explain", "jinish"]):
        text = f"📘 **Details:** {info['en'] if not is_bangla else info['bn']}"
        ans.append(text)

    # ২. ডাক্তার বা চিকিৎসা নিয়ে প্রশ্ন করলে
    if any(w in q for w in ["doctor", "valo", "val", "dakhtar", "dekha", "hospital", "treat", "solve"]):
        text = "👨‍⚕️ **Medical Advice:** " + ("আপনার এই সমস্যার জন্য একজন চর্মরোগ বিশেষজ্ঞ (Dermatologist) দেখানো সবচেয়ে ভালো হবে।" if is_bangla else f"For {res}, consulting a professional Dermatologist is highly recommended.")
        ans.append(text)

    # ৩. ঔষধ নিয়ে প্রশ্ন করলে
    if any(w in q for w in ["medicine", "osud", "cream", "ঔষধ", "ointment"]):
        text = "⚠️ **Warning:** " + ("ডাক্তারের পরামর্শ ছাড়া কোনো মলম বা ঔষধ ব্যবহার করবেন না। এটি আপনার ত্বকের ক্ষতি করতে পারে।" if is_bangla else "Do not apply any creams or medicines without a doctor's prescription.")
        ans.append(text)

    # ৪. কারণ জানতে চাইলে
    if any(w in q for w in ["keno", "why", "cause", "hoyeche", "reason"]):
        text = f"🧬 **Cause:** " + (f"{res} মূলত সূর্যের অতিবেগুনি রশ্মি বা জেনেটিক কারণে হয়।" if is_bangla else f"{res} is often caused by prolonged UV exposure or genetic factors.")
        ans.append(text)

    if ans:
        return "\n\n---\n\n".join(ans)
    else:
        return f"আমি আপনার রিপোর্টে **{res}** শনাক্ত করেছি। আপনি কি এর বিস্তারিত বা প্রতিকার জানতে চান?" if is_bangla else f"I detected **{res}**. Would you like to know its causes or treatment options?"

# --- ৫. মডেল লোডিং ---
@st.cache_resource
def load_skin_model():
    path = 'skin_cancer_model.h5'
    if not os.path.exists(path): gdown.download(id='1JpKXUXu_DsXK5-uq7fpgg5aDY7hBhq9h', output=path, quiet=False)
    return tf.keras.models.load_model(path, compile=False)
model = load_skin_model()
classes = list(disease_info.keys())

# --- ৬. সেশন ও সাইডবার (Cleaned for duplication) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []
if 'last_res' not in st.session_state: st.session_state.last_res = "None"
if 'user' not in st.session_state: st.session_state.user = None

with st.sidebar:
    st.markdown('<div class="brand-card">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3591/3591147.png", width=90)
    st.markdown('<p class="wishy-tag">Developed by Wishy</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_res = "None"
        st.rerun()

    st.markdown("---")
    
    if not st.session_state.logged_in:
        t1, t2 = st.tabs(["🔑 Login", "🆕 Register"])
        with t1:
            e = st.text_input("Gmail", key="log_e")
            p = st.text_input("Password", type="password", key="log_p")
            if st.button("Enter Login", use_container_width=True):
                c.execute('SELECT password FROM users WHERE email=?', (e,))
                data = c.fetchone()
                if data and check_hash(p, data[0]):
                    st.session_state.logged_in, st.session_state.user = True, e
                    c.execute('SELECT role, content FROM chat_history WHERE email=?', (e,))
                    st.session_state.messages = [{"role": r, "content": ct} for r, ct in c.fetchall()]
                    st.success("History Loaded!"); time.sleep(0.5); st.rerun()
                else: st.error("Invalid credentials.")
        with t2:
            re = st.text_input("New Gmail", key="reg_e")
            rp = st.text_input("New Password", type="password", key="reg_p")
            if st.button("Sign Up", use_container_width=True):
                if "@" in re and len(rp) > 3:
                    try:
                        c.execute('INSERT INTO users VALUES (?,?)', (re, make_hash(rp))); conn.commit()
                        st.success("Registered! Please Login.")
                    except: st.error("User already exists.")
    else:
        st.success(f"Logged in: {st.session_state.user}")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False; st.session_state.messages = []; st.rerun()

    st.markdown("---")
    with st.expander("❓ Help & Info"):
        st.write("১. স্পষ্ট ছবি আপলোড করুন।")
        st.write("২. রিপোর্ট পাওয়ার পর প্রশ্ন করুন।")

# --- ৭. মেইন চ্যাট ইন্টারফেস ---
st.title("🩺 SkinAI Assistant")
file = st.file_uploader("Upload Skin Photo", type=["jpg", "png", "jpeg"])

if file:
    img = Image.open(file).convert('RGB')
    st.image(img, width=320)
    img_res = img.resize((100, 75))
    x = np.asarray(img_res) / 255.0; x = np.expand_dims(x, axis=0)
    pred = model.predict(x, verbose=0)
    st.session_state.last_res = classes[np.argmax(pred)]
    st.success(f"Detection Result: **{st.session_state.last_res}**")

st.markdown("---")
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Ask anything..."):
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
