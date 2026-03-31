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

# --- ৩. রোগের ডাটাবেস (৭টি রোগ) ---
disease_info = {
    'Actinic keratoses': {'bn': "এটি খসখসে রোদে পোড়া দাগ। এটি ক্যান্সার হওয়ার আগের ধাপ হতে পারে।", 'en': "Rough, scaly patches caused by sun exposure. It can be precancerous."},
    'Basal cell carcinoma': {'bn': "এটি সাধারণ স্কিন ক্যান্সার। এটি ধীরে বাড়ে কিন্তু চিকিৎসা জরুরি।", 'en': "A common skin cancer that grows slowly but needs medical treatment."},
    'Benign keratosis': {'bn': "এটি ক্ষতিকারক নয়। বয়সের কারণে ত্বকে এমন দাগ হতে পারে।", 'en': "Non-cancerous skin growth often related to aging."},
    'Dermatofibroma': {'bn': "এটি ত্বকের নিচে শক্ত ছোট পিণ্ড। সাধারণত ক্ষতিকর নয়।", 'en': "Small, firm skin growths that are usually harmless."},
    'Melanoma': {'bn': "এটি মারাত্মক স্কিন ক্যান্সার। দ্রুত বিশেষজ্ঞ ডাক্তার দেখান।", 'en': "The most serious type of skin cancer. Consult a specialist immediately."},
    'Nevus': {'bn': "এটি সাধারণ তিল। আকার বা রঙ বদলালে পরীক্ষা করুন।", 'en': "A common mole. Check if it changes shape or color rapidly."},
    'Vascular lesions': {'bn': "রক্তনালীর অস্বাভাবিকতায় লাল দাগ। সাধারণত বিপজ্জনক নয়।", 'en': "Red marks from abnormal blood vessels, usually harmless."}
}

# --- ৪. স্মার্ট মাল্টি-ল্যাঙ্গুয়েজ ও মাল্টি-অ্যানসার ইঞ্জিন (FIXED) ---
# --- ৪. স্মার্ট মাল্টি-ল্যাঙ্গুয়েজ ও মাল্টি-অ্যানসার ইঞ্জিন (Ultimate Fix) ---
def get_intelligent_response(query, res):
    with st.status("SkinAI is thinking...", expanded=False) as status:
        time.sleep(1.2)
        status.update(label="Analysis Done!", state="complete")
    
    q = query.lower()
    
    # ১. কঠোর ল্যাঙ্গুয়েজ ডিটেকশন
    # যদি বাংলা ক্যারেক্টার থাকে অথবা বাংলিশের একদম স্পেসিফিক শব্দ থাকে তবেই বাংলা হবে
    is_bangla = any('\u0980' <= char <= '\u09FF' for char in query) or \
                any(word in q.split() for word in ["ki", "keno", "ken", "hoyeche", "korbo", "eta", "eita", "osud", "bolun"])
    
    ans = []
    if res == "None":
        return "দয়া করে আগে একটি ছবি আপলোড করুন।" if is_bangla else "Please upload a photo first."

    info = disease_info.get(res, {})

    # ২. মাল্টি-কোয়েশ্চেন লজিক (একসাথে সব উত্তর দিবে)
    
    # বর্ণনা (Details)
    if any(w in q for w in ["ki", "what", "detail", "details", "বর্ণনা", "রোগ"]):
        if is_bangla:
            ans.append(f"📘 **বিস্তারিত:** {info['bn']}")
        else:
            ans.append(f"📘 **Details:** {info['en']}")

    # কারণ (Cause)
    if any(w in q for w in ["keno", "why", "cause", "হলো", "কারণ", "ken"]):
        if is_bangla:
            ans.append(f"🧬 **কারণ:** {res} মূলত সূর্যের অতিবেগুনি রশ্মি (UV) বা জীনগত পরিবর্তনের ফলে হয়।")
        else:
            ans.append(f"🧬 **Cause:** {res} is usually caused by prolonged UV radiation or genetic skin cell changes.")
            
    # সমাধান/ঔষধ (Medicine)
    if any(w in q for w in ["osud", "medicine", "solution", "ঔষধ", "treat", "doctor", "treatment"]):
        if is_bangla:
            ans.append(f"⚠️ **পরামর্শ:** বিশেষজ্ঞ ডাক্তারের অনুমতি ছাড়া কোনো ঔষধ বা ক্রিম ব্যবহার করবেন না।")
        else:
            ans.append(f"⚠️ **Suggestion:** Do not use any medication or treatment without consulting a dermatologist.")
    
    # ৩. ফাইনাল রেজাল্ট ডেলিভারি
    if ans:
        return "\n\n---\n\n".join(ans)
    else:
        # কোনো কি-ওয়ার্ড না মিললে ডিফল্ট রিপ্লাই
        if is_bangla:
            return f"আমি রিপোর্টে **{res}** শনাক্ত করেছি। আপনি কি এর বিস্তারিত বা প্রতিকার জানতে চান?"
        else:
            return f"I detected **{res}** in your report. Would you like to know its details or treatment?"
# --- ৫. মডেল লোডিং ---
@st.cache_resource
def load_skin_model():
    path = 'skin_cancer_model.h5'
    if not os.path.exists(path): gdown.download(id='1JpKXUXu_DsXK5-uq7fpgg5aDY7hBhq9h', output=path, quiet=False)
    return tf.keras.models.load_model(path, compile=False)

model = load_skin_model()
classes = list(disease_info.keys())
# --- ৬. সেশন ও সাইডবার ম্যানেজমেন্ট ---
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
        st.rerun()

    st.markdown("---")
    
    # এখন এটি চেক করলে আর এরর আসবে না
    if not st.session_state.logged_in:
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    
    if not st.session_state.logged_in:
        # সোশ্যাল বাটন (প্রেজেন্টেশন মোড)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔵 Facebook", use_container_width=True): st.info("Coming Soon!")
        with col2:
            if st.button("🔴 Gmail", use_container_width=True): st.info("Coming Soon!")
        
        st.markdown("---")
        tab1, tab2 = st.tabs(["🔑 Login", "🆕 Create Account"])
        
        with tab1:
            l_email = st.text_input("Gmail", key="l_email")
            l_pass = st.text_input("Password", type="password", key="l_pass")
            if st.button("Enter Login", use_container_width=True):
                c.execute('SELECT password FROM users WHERE email=?', (l_email,))
                data = c.fetchone()
                
                if data and check_hash(l_pass, data[0]):
                    # সেশন সেট করা
                    st.session_state.logged_in = True
                    st.session_state.user = l_email
                    
                    # --- ডাটাবেস থেকে হিস্ট্রি রিট্রিভ করা ---
                    c.execute('SELECT role, content FROM chat_history WHERE email=?', (l_email,))
                    all_messages = c.fetchall()
                    
                    # সেশন মেসেজ লিস্টে ডাটাবেসের মেসেজগুলো পুশ করা
                    st.session_state.messages = []
                    for role, content in all_messages:
                        st.session_state.messages.append({"role": role, "content": content})
                    
                    st.success("History Loaded!")
                    time.sleep(0.5)
                    st.rerun() # পেজ রিফ্রেশ দিয়ে হিস্ট্রি দেখানো
                else:
                    st.error("Invalid Login.")
                
        with tab2:
            s_email = st.text_input("New Gmail", key="s_email")
            s_pass = st.text_input("New Password", type="password", key="s_pass")
            if st.button("Sign Up", use_container_width=True):
                if "@" in s_email and len(s_pass) >= 4:
                    try:
                        c.execute('INSERT INTO users VALUES (?,?)', (s_email, make_hash(s_pass))); conn.commit()
                        st.success("Done! Now Login.")
                    except: st.error("User exists.")
                else: st.warning("Enter valid details.")
    else:
        st.success(f"Logged in as: {st.session_state.user}")
        if st.button("Logout", use_container_width=True): 
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")
    with st.expander("⚙️ Settings"): st.write("v32.0 - History Enabled")

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
