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

# --- ২. ডিজাইন ---
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

# --- ৪. স্মার্ট রিপ্লাই ইঞ্জিন (Smart Context Added) ---
def get_intelligent_response(query, res):
    with st.status("Analyzing...", expanded=False) as status:
        time.sleep(1.0)
        status.update(label="Analysis Done!", state="complete")
    
    q = query.lower()
    is_bangla = any('\u0980' <= char <= '\u09FF' for char in query) or \
                any(word in q.split() for word in ["ki", "keno", "ken", "eta", "bolo", "hoyeche", "yes", "ha"])
    
    if res == "None":
        return "দয়া করে আগে একটি ছবি আপলোড করুন।" if is_bangla else "Please upload a photo first."

    info = disease_info.get(res, {})
    ans = []

    # স্মার্ট লজিক: ইউজার যদি বিস্তারিত বা "yes/বলো" টাইপ কিছু বলে
    if any(w in q for w in ["ki", "what", "detail", "yes", "ha", "bolo", "bolun", "explain"]):
        ans.append(f"📘 **Details:** {info['bn'] if is_bangla else info['en']}")

    # ঘরোয়া টিপস
    if any(w in q for w in ["ghoroya", "home", "remedy", "tips", "upai", "bashay"]):
        text = ("🏠 **ঘরোয়া পরামর্শ:** রোদ থেকে দূরে থাকুন, আক্রান্ত স্থান খুঁটবেন না এবং পর্যাপ্ত পানি পান করুন।") if is_bangla else ("🏠 **Home Tips:** Avoid UV exposure and keep the area clean.")
        ans.append(text)

    # ডাক্তার/চিকিৎসা
    if any(w in q for w in ["doctor", "dakhtar", "treat", "valo", "medicine", "osud"]):
        text = ("👨‍⚕️ **পরামর্শ:** ডাক্তারের পরামর্শ ছাড়া কোনো ঔষধ ব্যবহার করবেন না। একজন চর্মরোগ বিশেষজ্ঞ দেখান।") if is_bangla else ("👨‍⚕️ **Advice:** Consult a Dermatologist before using any medicine.")
        ans.append(text)

    if ans:
        return "\n\n---\n\n".join(ans)
    else:
        return f"আমি আপনার রিপোর্টে **{res}** শনাক্ত করেছি। আপনি কি এর বিস্তারিত বা ঘরোয়া টিপস জানতে চান?" if is_bangla else f"I detected **{res}**. Would you like its details or home tips?"

# --- ৫. মডেল লোড ---
@st.cache_resource
def load_skin_model():
    path = 'skin_cancer_model.h5'
    if not os.path.exists(path): gdown.download(id='1JpKXUXu_DsXK5-uq7fpgg5aDY7hBhq9h', output=path, quiet=False)
    return tf.keras.models.load_model(path, compile=False)
model = load_skin_model()
classes = list(disease_info.keys())

# --- ৬. সেশন ও সাইডবার ---
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
            e = st.text_input("Gmail", key="l_e")
            p = st.text_input("Password", type="password", key="l_p")
            if st.button("Login", use_container_width=True):
                c.execute('SELECT password FROM users WHERE email=?', (e,))
                data = c.fetchone()
                if data and check_hash(p, data[0]):
                    st.session_state.logged_in, st.session_state.user = True, e
                    c.execute('SELECT role, content FROM chat_history WHERE email=?', (e,))
                    st.session_state.messages = [{"role": r, "content": ct} for r, ct in c.fetchall()]
                    st.success("History Loaded!"); time.sleep(0.5); st.rerun()
        with t2:
            re = st.text_input("New Gmail", key="r_e")
            rp = st.text_input("New Pass", type="password", key="r_p")
            if st.button("Sign Up", use_container_width=True):
                if "@" in re and len(rp) > 3:
                    try:
                        c.execute('INSERT INTO users VALUES (?,?)', (re, make_hash(rp))); conn.commit()
                        st.success("Done! Login now.")
                    except: st.error("Exists.")
    else:
        st.success(f"User: {st.session_state.user}")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False; st.session_state.messages = []; st.rerun()

# --- ৭. মেইন ইন্টারফেস ---
st.title("🩺 SkinAI Assistant")
file = st.file_uploader("Upload Skin Photo", type=["jpg", "png", "jpeg"])

if file:
    img = Image.open(file).convert('RGB')
    st.image(img, width=320)
    img_res = img.resize((100, 75))
    x = np.asarray(img_res) / 255.0; x = np.expand_dims(x, axis=0)
    pred = model.predict(x, verbose=0)
    st.session_state.last_res = classes[np.argmax(pred)]
    st.success(f"Detection: **{st.session_state.last_res}**")

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
