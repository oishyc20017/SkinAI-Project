import streamlit as st
import requests
from streamlit_lottie import st_lottie
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
    /* ১. তোমার সেই সুন্দর টাইটেলগুলো (অপরিবর্তিত) */
    .rainbow-text {
        background: linear-gradient(to right, #ef5350, #f48fb1, #7e57c2, #2196f3, #26c6da, #43a047, #eeff41, #f9a825, #ff5722);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 400% 400%;
        animation: rainbow 8s ease infinite;
        font-weight: 800;
        font-size: 38px;
        text-align: center;
        display: block;
    }
    .wishy-tag {
    font-family: 'Dancing Script', cursive, sans-serif; /* কার্সিভ ফন্ট */
    font-weight: 600;
    font-size: 18px;
    background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    display: block;
    letter-spacing: 1px;
    margin-top: -5px;
}

    /* ২. জেমিনি লুক: ডিফল্ট বর্ডার এবং কালার পুরোপুরি ভ্যানিশ করা */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* চ্যাট মেসেজের ভেতরের ডিফল্ট বক্স রিমুভ */
    [data-testid="stChatMessage"] > div {
        background-color: transparent !important;
        border: none !important;
    }

    /* ৩. জেমিনি স্টাইল চ্যাট বাবল (স্মুথ লুক) */
    .chat-bubble {
        background-color: #1e1f20; /* জেমিনি ডার্ক গ্রে */
        border: 1px solid #3c4043;
        border-radius: 20px;
        padding: 16px 20px;
        color: #e3e3e3;
        line-height: 1.6;
        margin-top: 5px;
        display: inline-block;
        max-width: 90%;
    }

    /* ৪. ইনপুট বক্স জেমিনি স্টাইল (গোল এবং ক্লিন) */
    [data-testid="stChatInput"] {
        border-radius: 30px !important;
        background-color: #1e1f20 !important;
        border: 1px solid #3c4043 !important;
    }

    /* ইনপুটের সেই লাল/কমলা বর্ডার ফোকাস সল্ভ করা */
    [data-testid="stChatInput"] div {
        border: none !important;
        box-shadow: none !important;
    }

    @keyframes rainbow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
</style>
""", unsafe_allow_html=True)

# --- ৩. রোগের বিস্তারিত ডাটাবেস (সাতটি রোগ) ---
disease_details = {
    'Actinic keratoses': {
        'desc': "এটি রোদে পোড়া খসখসে দাগ। এটি অবহেলা করলে ভবিষ্যতে ক্যান্সার হতে পারে।",
        'cause': "দীর্ঘদিন সূর্যের অতিবেগুনি রশ্মির (UV) সংস্পর্শে থাকা।",
        'home': "রোদে বের হওয়া কমিয়ে দিন, সানস্ক্রিন ব্যবহার করুন এবং আক্রান্ত স্থান ময়েশ্চারাইজড রাখুন।",
        'advice': "একজন চর্মরোগ বিশেষজ্ঞকে দেখিয়ে নিশ্চিত হোন যে এটি ক্যান্সারের দিকে যাচ্ছে কি না।"
    },
    'Basal cell carcinoma': {
        'desc': "এটি একটি সাধারণ স্কিন ক্যান্সার। এটি সাধারণত শরীরের খোলা অংশে দেখা দেয়।",
        'cause': "সূর্যের আলো বা ট্যানিং বেড থেকে আসা UV রশ্মি।",
        'home': "বাসায় এর কোনো প্রতিকার নেই, তবে ত্বক পরিষ্কার রাখুন এবং চিকিৎসকের পরামর্শ নিন।",
        'advice': "বায়োপসি বা ছোট সার্জারির প্রয়োজন হতে পারে। দ্রুত ডাক্তার দেখান।"
    },
    'Benign keratosis': {
        'desc': "এটি ক্ষতিকর নয়। সাধারণত বয়সের সাথে সাথে ত্বকে তিল বা আঁচিলের মতো কালো দাগ পড়ে।",
        'cause': "বয়স বৃদ্ধি এবং কিছুটা জীনগত কারণ।",
        'home': "নারিকেল তেল বা ময়েশ্চারাইজার লাগাতে পারেন যদি চুলকানি হয়।",
        'advice': "সাধারণত চিকিৎসার দরকার নেই, তবে দাগটি দ্রুত বড় হলে ডাক্তার দেখান।"
    },
    'Dermatofibroma': {
        'desc': "ত্বকের নিচে ছোট শক্ত গুটির মতো। এটি ম্যালিগন্যান্ট বা ক্ষতিকর নয়।",
        'cause': "পোকার কামড় বা ছোট কোনো আঘাতের প্রতিক্রিয়া।",
        'home': "খুঁটবেন না। এটি নিজে থেকেই শক্ত হয়ে থাকে।",
        'advice': "যদি ব্যথা হয় বা অস্বস্তি লাগে তবে ডাক্তার দেখিয়ে অপসারণ করতে পারেন।"
    },
    'Melanoma': {
        'desc': "সবচেয়ে মারাত্মক স্কিন ক্যান্সার। এটি দ্রুত শরীরের অন্য অংশে ছড়িয়ে পড়ে।",
        'cause': "জেনেটিক মিউটেশন এবং তীব্র রোদে পোড়া।",
        'home': "ঘরোয়া কোনো চিকিৎসা নেই। সময় নষ্ট করা বিপজ্জনক।",
        'advice': "জরুরি ভিত্তিতে একজন অনকোলজিস্ট বা ডার্মাটোলজিস্ট দেখান।"
    },
    'Nevus': {
        'desc': "এটি আমাদের পরিচিত সাধারণ তিল। এটি নিয়ে চিন্তার কিছু নেই।",
        'cause': "ত্বকের মেলানিন কোষগুলো এক জায়গায় জমা হওয়া।",
        'home': "সূর্যের রোদ থেকে বাঁচলে নতুন তিল পড়া কমে।",
        'advice': "যদি তিলের আকার বা রঙ হঠাৎ বদলে যায়, তবেই ডাক্তার দেখান।"
    },
    'Vascular lesions': {
        'desc': "রক্তনালীর অস্বাভাবিকতার কারণে লাল বা বেগুনি দাগ।",
        'cause': "জন্মগত কারণ বা রক্তনালীর প্রসারণ।",
        'home': "বরফ দিতে পারেন যদি সামান্য ফোলা থাকে, তবে এটি স্থায়ী সমাধান নয়।",
        'advice': "লেজার ট্রিটমেন্টের মাধ্যমে এটি পুরোপুরি দূর করা সম্ভব।"
    }
}

# --- ৪. ইন্টেলিজেন্ট ল্যাঙ্গুয়েজ সুইচ ইঞ্জিন (Fix: English vs Bangla/Banglish) ---
def get_intelligent_response(query, res):
    with st.status("Analyzing your question...", expanded=False) as status:
        time.sleep(1.0)
        status.update(label="Response Ready!", state="complete")
    
    q = query.lower()
    if res == "None":
        is_bn = any('\u0980' <= char <= '\u09FF' for char in query) or any(word in q for word in ["ki", "keno", "upai"])
        return "দয়া করে আগে একটি ছবি আপলোড করুন।" if is_bn else "Please upload a photo first."

    data = disease_details.get(res, {})
    
    # বাংলা এবং বাংলিশ কী-ওয়ার্ড চেক
    bangla_hints = ["ki", "keno", "ken", "bolo", "tips", "bashay", "osud", "doctor", "upai", "goroa", "protikar"]
    is_bangla_script = any('\u0980' <= char <= '\u09FF' for char in query)
    is_banglish = any(word in q.split() for word in bangla_hints) # split() দিলে একদম সঠিক শব্দ ধরবে

    # যদি ইউজার বাংলা বা বাংলিশ ব্যবহার করে
    if is_bangla_script or is_banglish:
        response = f"### 🩺 **AI বিশ্লেষণ: {res}**\n\n"
        response += f"**১. এটি আসলে কী?**\n{data['desc']}\n\n"
        response += f"**২. এটি কেন হয়?**\n{data['cause']}\n\n"
        response += f"**৩. ঘরোয়া টিপস ও সাবধানতা:**\n{data['home']}\n\n"
        response += f"**৪. বিশেষজ্ঞের পরামর্শ:**\n{data['advice']}\n\n"
        response += "---\n*আপনার কি আরও কিছু জানার আছে?*"
    
    # যদি ইউজার পুরোপুরি ইংরেজিতে প্রশ্ন করে (যেমন: "What is this?", "Give me details")
    else:
        response = f"### 🩺 **AI Analysis: {res}**\n\n"
        response += f"**1. What is it?**\nIt is identified as {res}. This condition causes changes in skin texture.\n\n"
        response += f"**2. Possible Causes:**\nUsually caused by prolonged UV exposure, genetic factors, or skin irritation.\n\n"
        response += f"**3. Home Care Tips:**\nAvoid direct sunlight, use high SPF sunscreen, and keep the skin moisturized.\n\n"
        response += f"**4. Medical Advice:**\nConsult a dermatologist for a professional clinical examination.\n\n"
        response += "---\n*Do you have any more questions about this?*"
    
    return response
# --- ৫. মডেল লোডিং ---
@st.cache_resource
def load_skin_model():
    path = 'skin_cancer_model.h5'
    if not os.path.exists(path): gdown.download(id='1JpKXUXu_DsXK5-uq7fpgg5aDY7hBhq9h', output=path, quiet=False)
    return tf.keras.models.load_model(path, compile=False)
model = load_skin_model()
classes = list(disease_details.keys())

# --- ৬. সেশন ও সাইডবার ম্যানেজমেন্ট (Buttons & History Fixed) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []
if 'last_res' not in st.session_state: st.session_state.last_res = "None"
if 'user' not in st.session_state: st.session_state.user = None

with st.sidebar:
    # --- লোগো সেন্টার এবং আধুনিক স্কিন এআই ডিজাইন ---
    st.write("") 
    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2:
        # এটি একটি রঙিন 'Skin Scan' বা 'Healthy Skin' আইকন
        st.image("https://cdn-icons-png.flaticon.com/512/3591/3591234.png", width=100)
    
    st.markdown("<br>", unsafe_allow_html=True) 
    # --- লোগোর নিচের গ্যাপ কমানো এবং টেক্সট কার্ড ---
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(88, 166, 255, 0.1) 0%, rgba(245, 87, 108, 0.1) 100%);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        margin-top: -10px;
    ">
        <p style="color: #e3e3e3; font-size: 13px; font-weight: 500; margin: 0; line-height: 1.4;">
            ✨ <span style="color: #58a6ff;">SkinAI</span> scans for 7 types of skin conditions with professional precision.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_res = "None"
        st.rerun()

    st.markdown("---")
    
    if not st.session_state.logged_in:
        # --- তোমার চাওয়া Facebook ও Gmail বাটন ---
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔵 Facebook", use_container_width=True): st.info("Coming Soon!")
        with col2:
            if st.button("🔴 Gmail", use_container_width=True): st.info("Coming Soon!")
        
        st.markdown("---")
        t1, t2 = st.tabs(["🔑 Login", "🆕 Register"])
        with t1:
            e = st.text_input("Gmail Address", key="l_e")
            p = st.text_input("Password", type="password", key="l_p")
            if st.button("Log In", use_container_width=True):
                c.execute('SELECT password FROM users WHERE email=?', (e,))
                data = c.fetchone()
                if data and check_hash(p, data[0]):
                    st.session_state.logged_in, st.session_state.user = True, e
                    # ডাটাবেস থেকে পুরনো হিস্ট্রি নিয়ে আসা
                    c.execute('SELECT role, content FROM chat_history WHERE email=?', (e,))
                    st.session_state.messages = [{"role": r, "content": ct} for r, ct in c.fetchall()]
                    st.success("Welcome back! History Loaded.")
                    time.sleep(0.5); st.rerun()
                else: st.error("Invalid Login Details.")
        with t2:
            re = st.text_input("New Gmail", key="r_e")
            rp = st.text_input("New Password", type="password", key="r_p")
            if st.button("Create Account", use_container_width=True):
                if "@" in re and len(rp) > 3:
                    try:
                        c.execute('INSERT INTO users VALUES (?,?)', (re, make_hash(rp))); conn.commit()
                        st.success("Account Created! Now Login.")
                    except: st.error("User already exists.")
                else: st.warning("Enter valid details.")
    else:
        st.success(f"Logged in as: {st.session_state.user}")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")
    with st.expander("❓ Help & Information"):
        st.write("১. স্পষ্ট ছবি আপলোড করুন।")
        st.write("২. রিপোর্ট পাওয়ার পর প্রশ্ন করুন।")
        st.write("৩. হিস্ট্রি দেখতে অবশ্যই লগইন করুন।")
# --- ৭. মেইন চ্যাট ইন্টারফেস ---
# আগের টাইটেল লাইনটি মুছে এই দুইটা লাইন দাও
# --- মেইন পেজ অ্যানিমেশন (টাইটেলের উপরে) ---
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if lottie_skin_ai:
        st_lottie(lottie_skin_ai, height=200, key="skin_anim")
    else:
        st.info("Loading Aesthetic Animation...")

# এর নিচেই তোমার আগের টাইটেল কোড থাকব
# --- অ্যানিমেশন লোড এবং দেখানো একসাথেই ---
import requests
from streamlit_lottie import st_lottie

def load_lottieurl(url):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_skin_ai = load_lottieurl("https://lottie.host/8040d75a-5262-4217-a9a7-961453a25d2a/T87hS79p1U.json")

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_skin_ai = load_lottieurl("https://lottie.host/8040d75a-5262-4217-a9a7-961453a25d2a/T87hS79p1U.json")
st.markdown(f'<h1 class="rainbow-text">SkinAI Assistant</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="wishy-tag">Developed by Wishy</p>', unsafe_allow_html=True)
st.markdown('<h1 class="rainbow-text">SkinAI Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="wishy-tag">Developed by Wishy</p>', unsafe_allow_html=True)
file = st.file_uploader("Upload Skin Photo", type=["jpg", "png", "jpeg"])

if file:
    img = Image.open(file).convert('RGB')
    st.image(img, width=320)
    img_res = img.resize((100, 75))
    x = np.asarray(img_res) / 255.0; x = np.expand_dims(x, axis=0)
    pred = model.predict(x, verbose=0)
    st.session_state.last_res = classes[np.argmax(pred)]
    # --- গর্জিয়াস রেজাল্ট ডিজাইন শুরু ---
    st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
        padding: 25px;
        border-radius: 15px;
        border-left: 6px solid #58a6ff;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
        margin: 25px 0;
        text-align: center;
    ">
        <p style="color: #8b949e; font-size: 13px; text-transform: uppercase; letter-spacing: 2px; margin: 0; font-weight: 600;">
            AI Diagnostic Analysis
        </p>
        <h1 style="color: #ffffff; margin: 15px 0; font-family: 'Segoe UI', sans-serif; font-size: 28px; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">
            🔍 {st.session_state.last_res}
        </h1>
        <div style="display: inline-block; padding: 6px 18px; background: rgba(88, 166, 255, 0.15); border: 1px solid rgba(88, 166, 255, 0.3); border-radius: 30px;">
            <span style="color: #58a6ff; font-size: 14px; font-weight: 500;">✨ Professional Grade Detection</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
  # --- গর্জিয়াস রেজাল্ট ডিজাইন শেষ ---

st.markdown("---")
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Ask me anything about your skin..."):
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
