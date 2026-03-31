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
conn = sqlite3.connect('skinai_wishy_v16.db', check_same_thread=False)
c = conn.cursor()
def init_db():
    c.execute('CREATE TABLE IF NOT EXISTS users(email TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS chat_history(email TEXT, role TEXT, content TEXT)')
    conn.commit()
init_db()

def make_hash(password): return hashlib.sha256(str.encode(password)).hexdigest()
def check_hash(p, h): return h if make_hash(p) == h else False

# --- ২. এস্থেটিক ডিজাইন ---
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e3e3e3; }
    [data-testid="stSidebar"] { background-color: #1e1f20 !important; border-right: 1px solid #30363d; }
    .brand-card {
        padding: 20px; border-radius: 15px; background: rgba(88, 166, 255, 0.05);
        border: 1px solid rgba(88, 166, 255, 0.2); text-align: center; margin-bottom: 25px;
    }
    .wishy-tag { font-size: 11px; color: #58a6ff; letter-spacing: 2.1px; font-weight: 800; margin-top: 10px; text-transform: uppercase; }
    .social-btn { background: white; color: black; padding: 8px; border-radius: 5px; text-align: center; margin-bottom: 8px; font-size: 14px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- ৩. রোগের নলেজ বেস (৭টি রোগ) ---
disease_info = {
    'Actinic keratoses': {
        'bn': "এটি মূলত রোদে পোড়া খসখসে দাগ। এটি ক্যান্সারের পূর্বাবস্থা হতে পারে। রোদ থেকে দূরে থাকুন।",
        'en': "Rough, scaly patches caused by years of sun exposure. Can be precancerous."
    },
    'Basal cell carcinoma': {
        'bn': "এটি এক ধরণের সাধারণ স্কিন ক্যান্সার। এটি ধীরে ধীরে বাড়ে কিন্তু ছড়িয়ে পড়ে না। সার্জারি প্রয়োজন হতে পারে।",
        'en': "A common type of skin cancer that grows slowly but rarely spreads. Surgery is often needed."
    },
    'Benign keratosis': {
        'bn': "এটি ক্ষতিকারক নয় (Non-cancerous)। বয়স বাড়লে ত্বকে এমন তিলের মতো দাগ হতে পারে।",
        'en': "Non-cancerous skin growth that can look like a mole or wart as people age."
    },
    'Dermatofibroma': {
        'bn': "এটি ত্বকের নিচে ছোট শক্ত পিণ্ড। সাধারণত ক্ষতিকর নয়, তবে ব্যথা থাকলে ডাক্তার দেখান।",
        'en': "Small, firm skin growths that are typically harmless but can be tender."
    },
    'Melanoma': {
        'bn': "এটি সবচেয়ে মারাত্মক স্কিন ক্যান্সার। দ্রুত ডার্মাটোলজিস্ট দেখান এবং বায়োপসি করান।",
        'en': "The most serious type of skin cancer. Requires immediate medical attention and biopsy."
    },
    'Nevus': {
        'bn': "এটি সাধারণ তিল। তবে তিলের রঙ বা আকার পরিবর্তন হলে পরীক্ষা করানো উচিত।",
        'en': "A common mole. Keep an eye on any changes in its shape, size, or color."
    },
    'Vascular lesions': {
        'bn': "এটি রক্তনালীর অস্বাভাবিকতার কারণে লাল দাগ বা জালের মতো দেখায়। এটি সাধারণত জন্মগত বা বয়সের কারণে হয়।",
        'en': "Skin marks caused by abnormal blood vessels, often red or purple in color."
    }
}

# --- ৪. স্মার্ট এআই ইঞ্জিন (Language + 7 Disease Logic) ---
def get_advanced_response(query, res):
    with st.status("SkinAI is thinking...", expanded=False) as status:
        time.sleep(1.8)
        status.update(label="Analysis Done!", state="complete")
    
    q = query.lower()
    is_bangla = any(char > '\u0980' and char < '\u09FF' for char in query)
    ans = []

    # যদি ডায়াগনোসিস না হয়ে থাকে
    if res == "None":
        return "দয়া করে আগে একটি ছবি আপলোড করুন।" if is_bangla else "Please upload a photo first."

    # রোগের বর্ণনা
    if any(w in q for w in ["ki", "what", "detail", "details", "বর্ণনা", "রোগ"]):
        info = disease_info.get(res, {})
        ans.append(f"📘 **Details:** {info['bn' if is_bangla else 'en']}")

    # কেন হয়েছে (Cause)
    if any(w in q for w in ["keno", "why", "cause", "হলো", "কারণ"]):
        if is_bangla:
            ans.append(f"🧬 **কারণ:** {res} মূলত দীর্ঘ সময় রোদে থাকা বা ত্বকের জীনগত পরিবর্তনের ফলে হয়।")
        else:
            ans.append(f"🧬 **Cause:** {res} is usually caused by UV rays or genetic skin cell changes.")
            
    # ঔষধ কি (Medicine)
    if any(w in q for w in ["osud", "medicine", "solution", "ঔষধ", "প্রতিকার"]):
        if is_bangla:
            ans.append(f"⚠️ **সতর্কতা:** ডাক্তারের পরামর্শ ছাড়া কোনো ঔষধ ব্যবহার করবেন না।")
        else:
            ans.append(f"⚠️ **Caution:** Consult a dermatologist before applying any medication.")
    
    if not ans:
        return f"আমি আপনার ছবিতে **{res}** শনাক্ত করেছি। এর বর্ণনা বা ঔষধ সম্পর্কে জানতে চান?" if is_bangla else f"I detected **{res}**. Want to know details or treatment?"
            
    return "\n\n---\n\n".join(ans)

# --- ৫. মডেল লোডিং ---
@st.cache_resource
def load_original_model():
    file_id = '1JpKXUXu_DsXK5-uq7fpgg5aDY7hBhq9h'
    model_path = 'skin_cancer_model.h5'
    if not os.path.exists(model_path):
        try: gdown.download(id=file_id, output=model_path, quiet=False, fuzzy=True)
        except: return None
    return tf.keras.models.load_model(model_path, compile=False)

model = load_original_model()
classes = list(disease_info.keys())

# --- ৬. সেশন ও সাইডবার ---
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
        with st.expander("👤 Account Login"):
            st.markdown('<div class="social-btn">🔵 Facebook</div><div class="social-btn">🔴 Gmail</div>', unsafe_allow_html=True)
            mode = st.radio("Mode", ["Login", "Sign Up"])
            u_email = st.text_input("Email")
            u_pass = st.text_input("Password", type="password")
            if st.button("Enter"):
                if mode == "Sign Up":
                    c.execute('INSERT INTO users VALUES (?,?)', (u_email, make_hash(u_pass)))
                    conn.commit()
                    st.success("Account Created!")
                else:
                    c.execute('SELECT password FROM users WHERE email=?', (u_email,))
                    data = c.fetchone()
                    if data and check_hash(u_pass, data[0]):
                        st.session_state.logged_in, st.session_state.user = True, u_email
                        c.execute('SELECT role, content FROM chat_history WHERE email=?', (u_email,))
                        st.session_state.messages = [{"role": r[0], "content": r[1]} for r in c.fetchall()]
                        st.rerun()
    else:
        st.info(f"User: {st.session_state.user}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("---")
    with st.expander("⚙️ Settings"): st.write("v16.0 Stable")
    with st.expander("❓ Help"): st.write("Upload clear skin photo.")

# --- ৭. মেইন কন্টেন্ট (সরাসরি চ্যাট) ---
st.title("🩺 SkinAI Assistant")

file = st.file_uploader("Upload Skin Photo", type=["jpg", "png", "jpeg"])
if file:
    img = Image.open(file).convert('RGB')
    st.image(img, width=320)
    if model:
        img_res = img.resize((100, 75))
        x = np.asarray(img_res) / 255.0
        x = np.expand_dims(x, axis=0)
        pred = model.predict(x, verbose=0)
        st.session_state.last_res = classes[np.argmax(pred)]
        st.success(f"Detection: **{st.session_state.last_res}**")

st.markdown("---")

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Type your message..."):
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
