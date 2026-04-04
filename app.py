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
    query = query.lower()
    
    # ১. চর্মরোগ নিয়ে প্রশ্ন করলে (মানুষের মতো পাল্টা প্রশ্ন)
    if any(word in query for word in ["দাগ", "চুলকানি", "skin", "rash", "problem", "সমস্যা", "লাল", "ব্যাথ", "জ্বালা"]):
        return (
            "আপনার সমস্যার কথা শুনে আমি বুঝতে পারছি আপনি কিছুটা অস্বস্তিতে আছেন। "
            "এই দাগ বা সমস্যাটি কি হঠাৎ করে হয়েছে নাকি অনেকদিন ধরে আছে? এটি কি খুব বেশি চুলকায় বা জ্বালাপোড়া করে?\n\n"
            "সঠিকভাবে জানার জন্য আপনি চাইলে নিচে থাকা **'Upload Skin Photo'** বাটন থেকে একটি ছবি দিতে পারেন। "
            "ছবি দিলে আমি এর **সাধারণ নাম** এবং **বৈজ্ঞানিক নাম**—দুটোই বলে দিতে পারবো।"
        )

    # ২. ছবি শনাক্ত হওয়ার পর সমাধান চাইলে
    if res and res != "None":
        if any(word in query for word in ["কিভাবে", "কি করবো", "solution", "প্রতিকার", "ভয়", "ওষুধ"]):
            return (
                f"শনাক্তকৃত সমস্যাটি হলো **{res}**। এটি সাধারণত ভয়ের কিছু নয়, তবে আপনার কি এটিতে ব্যথা বা অস্বস্তি অনুভব হয়? "
                "সাধারণত এটি দ্রুত ছড়ায় না। তবে আপনি চাইলে জায়গাটি পরিষ্কার রাখতে পারেন এবং নিশ্চিত হওয়ার জন্য একজন চর্মরোগ বিশেষজ্ঞকে দেখাতে পারেন।"
            )

    # ৩. হাই বা হ্যালো বললে (সহজ উত্তর)
    if any(word in query for word in ["hi", "hello", "হাই", "হ্যালো", "hey"]):
        return "হ্যালো! আমি আপনার ত্বকের সুরক্ষায় সাহায্য করতে এখানে আছি। আপনার ত্বকে কি কোনো সমস্যা দেখা দিয়েছে? আপনি চাইলে বিস্তারিত বলতে পারেন বা একটি ছবি আপলোড করতে পারেন।"

    # ৪. অন্য সব কিছুর জন্য সাধারণ রিপ্লাই
    return "আমি আপনার কথা বুঝতে পেরেছি। আপনার ত্বকের কোনো সমস্যা থাকলে আমাকে বিস্তারিত জানান, আমি সমাধান দেওয়ার চেষ্টা করবো।"

# --- ফাংশন এখানে শেষ ---

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
# --- ১. মেইন পেজ অ্যানিমেশন ---
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    try:
        import requests
        from streamlit_lottie import st_lottie
        
        def load_my_anim(url):
            res = requests.get(url)
            return res.json() if res.status_code == 200 else None

        # সঠিক লিঙ্ক দিয়ে অ্যানিমেশন লোড করা
        my_lottie_data = load_my_anim("https://lottie.host/8040d75a-5262-4217-a9a7-961453a25d2a/T87hS79p1U.json")

        if my_lottie_data:
            st_lottie(my_lottie_data, height=200, key="skin_scanner_anim")
    except:
        pass

# --- লোগো এবং টাইটেল (একদম মাঝখানে এবং ছোট) ---
# --- লোগো এবং স্টাইলিশ টাইটেল ---
# --- লোগো এবং বড় টাইটেল (একদম মাঝখানে) ---
st.markdown(
    """
    <div style="text-align: center; margin-top: -80px; margin-bottom: 10px;">
        <div style="display: flex; justify-content: center;">
            <img src="https://cdn-icons-png.flaticon.com/512/2808/2808549.png" width="80">
        </div>
        <h1 class="rainbow-text" style="margin: 10px 0 0 0; font-size: 45px; font-weight: 800; line-height: 1.1;">
            SkinAI Assistant
        </h1>
        <p class="wishy-tag" style="margin: 5px 0 0 0; font-size: 16px; font-weight: bold;">
            Developed by Wishy
        </p>
    </div>
    <hr style="margin-top: 5px; margin-bottom: 15px; border: 0.1px solid #444; opacity: 0.2;">
    """,
    unsafe_allow_html=True
)
file = st.file_uploader("Upload Skin Photo", type=["jpg", "png", "jpeg"])

# --- ইমেজ প্রসেসিং এবং রেজাল্ট ---
# --- ২. ইমেজ প্রসেসিং এবং বুদ্ধিমান রেজাল্ট ---
if file:
    import numpy as np
    img_res = Image.open(file).convert('RGB').resize((100, 75))
    x = np.asarray(img_res) / 255.0
    x = np.expand_dims(x, axis=0)
    pred = model.predict(x, verbose=0)
    res_name = classes[np.argmax(pred)]
    st.session_state.last_res = res_name

    # 🏥 রোগের নাম ও বিবরণ (মানুষ যেভাবে চেনে বনাম বৈজ্ঞানিক নাম)
    disease_info = {
        "Actinic keratoses": {"local": "রোদে পোড়া খসখসে দাগ", "desc": "এটি সূর্যরশ্মির কারণে হয়। অবহেলা করলে এটি ভবিষ্যতে ক্যান্সারে রূপ নিতে পারে।"},
        "Basal cell carcinoma": {"local": "সাধারণ স্কিন ক্যান্সার", "desc": "এটি ত্বকের কোষের এক প্রকার ক্যান্সার যা সাধারণত ধীরে ছড়ায়। ডাক্তারের পরামর্শ নিন।"},
        "Benign keratosis-like lesions": {"local": "ক্ষতিহীন আঁচিল বা তিল", "desc": "এটি সাধারণত ভয়ের কিছু নয়, ত্বকের স্বাভাবিক বৃদ্ধি মাত্র।"},
        "Dermatofibroma": {"local": "ত্বকের শক্ত গুটি", "desc": "ত্বকের নিচে ছোট শক্ত দানা। এটি ক্ষতিকর নয় তবে অস্বস্তি হতে পারে।"},
        "Melanocytic nevi": {"local": "সাধারণ তিল বা জন্মদাগ", "desc": "এটি আমাদের ত্বকের অতি পরিচিত তিল। তবে তিলের রঙ বা আকার দ্রুত বদলালে সতর্ক হন।"},
        "Melanoma": {"local": "মারাত্মক স্কিন ক্যান্সার", "desc": "এটি ত্বকের সবথেকে বিপজ্জনক ক্যান্সার। দ্রুত চর্মরোগ বিশেষজ্ঞের সাথে যোগাযোগ করুন।"},
        "Vascular lesions": {"local": "রক্তনালীর লাল দাগ", "desc": "জন্মগত লাল দাগ বা রক্তনালী ফুলে যাওয়া। এগুলো সাধারণত জটিল কোনো সমস্যা নয়।"}
    }

    # তথ্য খুঁজে বের করা
    info = disease_info.get(res_name, {"local": "অজানা সমস্যা", "desc": "এই সমস্যাটি সম্পর্কে বিস্তারিত তথ্য পাওয়া যায়নি।"})

    # --- ৩. সুন্দর রেজাল্ট কার্ড (তোমার ইচ্ছা মতো সাজানো) ---
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 30px; border-radius: 20px; border-left: 8px solid #58a6ff; box-shadow: 0 15px 35px rgba(0,0,0,0.5); margin: 25px 0; text-align: center;">
        <p style="color: #58a6ff; font-size: 14px; text-transform: uppercase; letter-spacing: 3px; font-weight: 700;">AI Diagnostic Analysis</p>
        
        <div style="margin: 20px 0;">
            <h4 style="color: #8b949e; margin-bottom: 5px; font-size: 16px;">মানুষ যেভাবে চেনে:</h4>
            <h1 style="color: #ffffff; font-size: 32px; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">{info['local']}</h1>
        </div>

        <div style="margin: 20px 0; border-top: 1px solid #334155; padding-top: 15px;">
            <p style="color: #8b949e; margin-bottom: 5px; font-size: 14px;">বৈজ্ঞানিক বা ডাক্তারি নাম:</p>
            <h3 style="color: #58a6ff; font-style: italic; font-size: 20px; margin: 0;">{res_name}</h3>
        </div>

        <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-top: 20px;">
            <p style="color: #cbd5e1; font-size: 15px; line-height: 1.6; margin: 0;">
                <b>বিবরণ:</b> {info['desc']}
            </p>
        </div>
        
        <p style="color: #ff7b72; font-size: 12px; margin-top: 20px; font-style: italic;">
            *এটি একটি AI ভিত্তিক ফলাফল। চূড়ান্ত সিদ্ধান্তের জন্য ডাক্তারের পরামর্শ নিন।
        </p>
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
        # রেজাল্ট কার্ড নয়, শুধু রোগের নাম পাঠাও যেন AI সুন্দর করে উত্তর দেয়
     clean_res = st.session_state.last_res if "last_res" in st.session_state else "None"
      reply = get_intelligent_response(prompt, clean_res)
       st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        if st.session_state.logged_in:
            c.execute('INSERT INTO chat_history VALUES (?,?,?)', (st.session_state.user, "assistant", reply)); conn.commit()
