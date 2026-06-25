import datetime
import re
import streamlit as st
import sqlite3
import smtplib
from email.message import EmailMessage
import requests # API দিয়ে SMS পাঠানোর জন্য
import hashlib
import requests
from streamlit_lottie import st_lottie
import time
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import gdown

API_KEY = "AIzaSyDdxIiL6woMlMxtQWlGSm3k3b93qp6XfRA"
genai.configure(api_key=API_KEY)
model_gemini = genai.GenerativeModel('gemini-1.5-flash')

# --- ৩. বাকি সব লজিক এবং ইউআই (এর নিচে) ---
st.set_page_config(page_title="SkinAI Pro", layout="wide")
# --- পেজ কনফিগারেশন (একটিই থাকবে) ---
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

# --- সাইডবার ও বাটন গোছানোর অ্যাডভান্সড সিএসএস ---
st.markdown("""
<style>
/* ১. বাটন স্টাইলিং */
div.stButton > button:first-child {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    color: white;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: bold;
    border: none;
    transition: all 0.3s ease;
}
div.stButton > button:first-child:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

/* ২. সাইডবার গোছানোর সিএসএস */
[data-testid="stSidebar"] {
    background-color: #0f172a !important; /* ডিপ ডার্ক প্রিমিয়াম ব্যাকগ্রাউন্ড */
    padding-top: 20px;
}

/* সাইডবারের ভেতরের ইনপুট বক্স充পেসিল স্পেসিং */
[data-testid="stSidebar"] .stTextInput, 
[data-testid="stSidebar"] .stSelectbox {
    margin-bottom: 20px !important;
}

/* সাইডবারের শিরোনাম কালার */
[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3 {
    color: #38bdf8 !important; 
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-weight: 600;
}

/* ডিভাইডার লাইন হালকা করা */
[data-testid="stSidebar"] hr {
    margin: 15px 0 !important;
    border-color: #334155 !important;
}

/* ৩. জেমিনি লুক: ডিফল্ট বর্ডার এবং কালার পুরোপুরি ভ্যানিশ করা */
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

/* ৪. জেমিনি স্টাইল চ্যাট বাবল (স্মুথ লুক) */
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

/* ৫. ইনপুট বক্স জেমিনি স্টাইল (গোল এবং ক্লিন) */
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
    font-family: 'Dancing Script', cursive, sans-serif;
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

@keyframes rainbow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
</style>
""", unsafe_allow_html=True)

# --- ১. ডাটাবেস ও সিকিউরিটি ---
conn = sqlite3.connect('skinai_wishy_v30.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    conn = sqlite3.connect('skinai_wishy_v30.db', check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_email TEXT, 
                  phone_number TEXT, 
                  doctor_name TEXT, 
                  date TEXT, 
                  time TEXT, 
                  status TEXT)''')
                  
    c.execute('''CREATE TABLE IF NOT EXISTS doctors
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT, specialty TEXT, fee TEXT, available_time TEXT)''')
                  
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (email TEXT, role TEXT, content TEXT)''')
    
    c.execute("SELECT COUNT(*) FROM doctors")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO doctors (name, specialty, fee, available_time) VALUES ('Dr. Sabina Yasmin', 'Dermatologist', '1000 BDT', '4:00 PM - 6:00 PM')")
        c.execute("INSERT INTO doctors (name, specialty, fee, available_time) VALUES ('Dr. Asif Ahmed', 'Skin & Laser Specialist', '1200 BDT', '7:00 PM - 9:00 PM')")
    
    conn.commit()
    conn.close()

init_db()

def make_hash(p): return hashlib.sha256(str.encode(p)).hexdigest()
def check_hash(p, h): return h if make_hash(p) == h else False

# --- ৩. রোগের বিস্তারিত ডাটাবেস ---
disease_details = {
    'Actinic keratoses': {
        'desc': "এটি রোদে পোড়া খসখসে দাগ। এটি অবহেলা করলে ভবিষ্যতে ক্যান্সার হতে পারে।",
        'cause': "দীর্ঘদিন সূর্যের অতিবেগুনি রশ্মির (UV) সংস্পর্শে থাকা।",
        'home': "রোদে বের হওয়া কমিয়ে দিন, সানস্ক্রিন ব্যবহার করুন এবং আক্রান্ত স্থান ময়েশ্চারাইজড রাখুন।",
        'advice': "একজন চর্মরোগ বিশেষজ্ঞকে দেখিয়ে নিশ্চিত হোন যে এটি ক্যান্সারের দিকে যাচ্ছে কি না।"
    },
    'Basal cell carcinoma': {
        'desc': "এটি একটি সাধারণ স্কিন ক্যান্সার। এটি সাধারণত শরীরের খোলা অংশে দেখা দেয়।",
        'cause': "সূর্যের আলো বা ট্যানিং বেড থেকে আসা UV রশ্মি।",
        'home': "বাসায় এর কোনো প্রতিকার নেই, তবে ত্বক পরিষ্কার রাখুন এবং চিকিৎসকের পরামর্শ নিন।",
        'advice': "বায়োপসি বা ছোট সার্জারির প্রয়োজন হতে পারে। দ্রুত ডাক্তার দেখান।"
    },
    'Benign keratosis': {
        'desc': "এটি ক্ষতিকর নয়। সাধারণত বয়সের সাথে সাথে ত্বকে تিল বা আঁচিলের মতো কালো দাগ পড়ে।",
        'cause': "বয়স বৃদ্ধি এবং কিছুটা জীনগত কারণ।",
        'home': "নারিকেল তেল বা ময়েশ্চারাইজার লাগাতে পারেন যদি চুলকানি হয়।",
        'advice': "সাধারণত চিকিৎসার দরকার নেই, তবে দাগটি দ্রুত বড় হলে ডাক্তার দেখান।"
    },
    'Dermatofibroma': {
        'desc': "ত্বকের নিচে ছোট শক্ত গুটির মতো। এটি ম্যালিгন্যান্ট বা ক্ষতিকর নয়।",
        'cause': "পোকার কামড় বা ছোট কোনো আঘাতের প্রতিক্রিয়া।",
        'home': "খুঁটবেন না। এটি নিজে থেকেই শক্ত হয়ে থাকে।",
        'advice': "যদি ব্যথা হয় বা অস্বস্তি লাগে তবে ডাক্তার দেখিয়ে অপসারণ করতে পারেন।"
    },
    'Melanoma': {
        'desc': "সবচেয়ে মারাত্মক স্কিন ক্যান্সার। এটি দ্রুত শরীরের অন্য অংশে ছড়িয়ে পড়ে।",
        'cause': "জেনেটিক মিউটেশন এবং তীব্র রোদে পোড়া।",
        'home': "ঘরোয়া কোনো চিকিৎসা নেই। সময় নষ্ট করা বিপজ্জনক।",
        'advice': "জরুরি ভিত্তিতে একজন অনকোলজিস্ট বা ডার্মাটোলজিস্ট দেখান।"
    },
    'Nevus': {
        'desc': "এটি আমাদের পরিচিত সাধারণ তিল। এটি নিয়ে চিন্তার কিছু নেই।",
        'cause': "ত্বকের মেলানিন কোষগুলো এক জায়গায় জমা হওয়া।",
        'home': "সূর্যের রোদ থেকে বাঁচলে নতুন তিল পড়া কমে।",
        'advice': "যদি তিলের আকার বা রঙ হঠাৎ বদলে যায়, তবেই ডাক্তার দেখান।"
    },
    'Vascular lesions': {
        'desc': "রক্তনালীর অস্বাভাবিকতার কারণে লাল বা বেগুনি দাগ।",
        'cause': "জন্মগত কারণ বা রক্তনালীর প্রসারণ।",
        'home': "বরফ দিতে পারেন যদি সামান্য ফোলা থাকে, তবে এটি স্থায়ী সমাধান নয়।",
        'advice': "লেজার ট্রিটমেন্টের মাধ্যমে এটি পুরোপুরি দূর করা সম্ভব।"
    }
}

# --- ৪. ইন্টেলিজেন্ট ল্যাঙ্গুয়েজ সুইচ ইঞ্জিন (ফিক্সড ও পারফেক্ট কন্ডিশন) ---
def get_intelligent_response(query, res):
    with st.status("Analyzing your question...", expanded=False) as status:
        time.sleep(1.0)
        status.update(label="Response Ready!", state="complete")
    
    q = query.lower()
    if res == "None":
        is_bn = any('\u0980' <= char <= '\u09FF' for char in query) or any(word in q for word in ["ki", "keno", "upai"])
        return "দয়া করে আগে একটি ছবি আপলোড করুন।" if is_bn else "Please upload a photo first."

    data = disease_details.get(res, {})
    
    is_bangla_script = any('\u0980' <= char <= '\u09FF' for char in query)
    bangla_hints = ["ki", "keno", "ken", "bolo", "tips", "bashay", "osud", "doctor", "upai", "goroa", "protikar", "valo", "daktar"]
    is_banglish = any(word in q.split() for word in bangla_hints)
    is_bn_mode = is_bangla_script or is_banglish

    # ১. নির্দিষ্ট নাম বা বেস্ট সাজেশনের হাই-প্রায়োরিটি কন্ডিশন
    if any(word in q for word in ["specific", "name", "nam", "tomar mote", "best", "kake", "kak", "mention"]):
        if is_bn_mode:
            personal_suggestions = [
                f"আমার ব্যক্তিগত মতামত চাইলে বলবো, আপনি আমাদের প্যানেলের সিনিয়র ডার্মাটোলজিস্ট **Dr. Sabina Yasmin** অথবা লেজার স্পেশালিস্ট **Dr. Asif Ahmed**-কে দেখাতে পারেন। ওনারা দুজনেই এই বিষয়ে বেশ অভিজ্ঞ।",
                f"যদি সুনির্দিষ্ট ১-২ জন ভালো ডাক্তারের কথা বলতে বলেন, তবে আমি সাজেস্ট করবো আপনি **Dr. Sabina Yasmin** অথবা **Dr. Nusrat Jahan**-এর অ্যাপয়েন্টমেন্ট নিতে পারেন।"
            ]
            return random.choice(personal_suggestions)
        else:
            personal_suggestions = [
                f"If you want specific recommendations, I highly suggest consulting **Dr. Sabina Yasmin** or **Dr. Asif Ahmed** from our panel. They are highly experienced with {res}.",
                f"Personally, scheduling a visit with either **Dr. Sabina Yasmin** or **Dr. Nusrat Jahan** would be the best choice for this condition."
            ]
            return random.choice(personal_suggestions)

    # ২. সাধারণ ক্যাটাগরি কন্ডিশন (কিসের ডাক্তার)
    elif any(word in q for word in ["doctor", "daktar", "dekhale", "specialist", "consult"]):
        if is_bn_mode:
            return f"যেহেতু এআই বিশ্লেষণে **{res}** এসেছে, এটি মূলত ত্বকের একটি বিশেষ সমস্যা। তাই এর জন্য আপনাকে অবশ্যই একজন **চর্মরোগ বিশেষজ্ঞ (Skin Specialist বা Dermatologist)** দেখাতে হবে। আপনার কি কোনো নির্দিষ্ট ডাক্তারের নাম জানার প্রয়োজন আছে?"
        else:
            return f"Since the analysis indicates **{res}**, this falls under skin-related pathologies. You should definitely consult a qualified **Dermatologist (Skin Specialist)**. Do you need any specific doctor names?"

    # ৩. কেন হয় বা কারণ কন্ডিশন
    elif any(word in q for word in ["keno", "ken", "cause", "caron", "bhav"]):
        if is_bn_mode:
            return f"এটি সাধারণত {data.get('cause', 'নির্দিষ্ট কিছু কারণে')} হয়ে থাকে। ত্বক সুরক্ষিত রাখতে কড়া রোদ থেকে দূরে থাকা ভালো। এই বিষয়ে কি আরও কোনো তথ্য আপনার প্রয়োজন?"
        else:
            return f"This condition is usually caused by {data.get('cause', 'various factors')}. Keep your skin shielded from UV rays. Do you need any further insights?"

    # ৪. ঘরোয়া চিকিৎসা কন্ডিশন
    elif any(word in q for word in ["home", "goroa", "tips", "bashay", "upai", "treatment", "upokar"]):
        if is_bn_mode:
            return f"বাসায় বসে আপনি যা করতে পারেন: {data.get('home', 'ত্বক পরিষ্কার ও ময়েশ্চারाइजড রাখুন।')}। তবে মনে রাখবেন, ঘরোয়া উপায় সাময়িক, মূল চিকিৎসার জন্য ডাক্তার দেখানোই শ্রেয়। আর কিছু কি জানতে চান?"
        else:
            return f"For temporary home care: {data.get('home', 'Keep the skin clean.')} However, professional diagnosis is highly recommended. Anything else I can help with?"

    # ৫. ডিফল্ট সাধারণ উত্তর
    else:
        if is_bn_mode:
            return f"আপনার আপলোড করা ছবিতে সম্ভবত **{res}** এর লক্ষণ দেখা যাচ্ছে। এটি মূলত {data.get('desc', 'একটি ত্বকের সমস্যা')}। আপনি কি এর কারণ বা কোন ডাক্তার দেখাবেন সে সম্পর্কে জানতে চান?"
        else:
            return f"Based on the image, it looks like **{res}**. {data.get('desc', 'This is a skin condition.')} Would you like to know about its causes or appropriate specialists?"
# --- ৫. モデル লোডিং ---
@st.cache_resource
def load_skin_model():
    path = 'skin_cancer_model.h5'
    if not os.path.exists(path): gdown.download(id='1JpKXUXu_DsXK5-uq7fpgg5aDY7hBhq9h', output=path, quiet=False)
    return tf.keras.models.load_model(path, compile=False)
model = load_skin_model()
classes = list(disease_details.keys())

# --- ৬. সেশন ও সাইডবার ম্যানেজমেন্ট (সম্পূর্ণ ইউনিক ও গোছানো) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []
if 'last_res' not in st.session_state: st.session_state.last_res = "None"
if 'user' not in st.session_state: st.session_state.user = None

with st.sidebar:
    # ১. লোগো এরিয়া
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3591/3591234.png", width=100)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    with st.expander("❓ Help & Information"):
        st.write("১. স্পষ্ট ছবি আপলোড করুন।")
        st.write("২. রিপোর্ট পাওয়ার পর প্রশ্ন করুন।")
        st.write("৩. হিস্ট্রি দেখতে অবশ্যই লগইন করুন।")

    # ২. সিকিউরিটি গেটওয়ে কার্ড
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%);
        padding: 15px; 
        border-radius: 10px; 
        border: 1px solid #4338ca; 
        text-align: center; 
        margin-bottom: 15px;">
        <h2 style="color: #38bdf8; margin: 0; font-size: 18px;">🔒 Secure Gateway</h2>
        <p style="color: #94a3b8; font-size: 11px; margin: 5px 0 0 0;">SHA-256 Encrypted Session</p>
    </div>
    """, unsafe_allow_html=True)

    # ৩. নিউ চ্যাট বাটন (সব এক লাইনে)
    if st.button("+ New Chat", use_container_width=True, key="unique_new_chat"): 
        st.session_state.messages = []
        st.session_state.last_res = "None"
        st.rerun()

    st.markdown("---")

    # ৪. ফেসবুক ও জিমেইল বাটন লজিক
    if not st.session_state.logged_in:
        st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 12px;'>Or Sign In With</p>", unsafe_allow_html=True)
        social_col1, social_col2 = st.columns(2)
        with social_col1:
            if st.button("🔵 Facebook", use_container_width=True, key="unique_fb"): st.info("Coming Soon!")
        with social_col2:
            if st.button("🔴 Gmail", use_container_width=True, key="unique_gm"): st.info("Coming Soon!")

        st.markdown("---")

        # ৫. আসল Login ও Register ট্যাব লজিক
        t1, t2 = st.tabs(["🔑 Login", "📝 Register"])
        
        with t1:
            e = st.text_input("✉️ Gmail Address", key="l_e", placeholder="username@gmail.com")
            p = st.text_input("🔑 Password", type="password", key="l_p", placeholder="••••••••")
            if st.button("Log In", use_container_width=True, key="unique_login_submit"):
                c.execute('SELECT password FROM users WHERE email=?', (e,))
                data = c.fetchone()
                if data and check_hash(p, data[0]):
                    st.session_state.logged_in = True
                    st.session_state.user = e
                    c.execute('SELECT role, content FROM chat_history WHERE email=?', (e,))
                    st.session_state.messages = [{"role": r, "content": ct} for r, ct in c.fetchall()]
                    st.success("Welcome back!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Invalid Login Details.")
                    
        with t2:
            r_name = st.text_input("👤 Full Name", key="r_name", placeholder="John Doe")
            re = st.text_input("✉️ New Gmail", key="r_e", placeholder="newuser@gmail.com")
            rp = st.text_input("🔑 New Password", type="password", key="r_p", placeholder="••••••••")
            
            if st.button("Create Account", use_container_width=True, key="unique_reg_submit"):
                if r_name == "":
                    st.warning("Please fill in your Full Name!")
                elif "@" in re and len(rp) > 3:
                    try:
                        c.execute('INSERT INTO users VALUES (?,?)', (re, make_hash(rp)))
                        conn.commit()
                        st.success(f"Account Created for {r_name}! Now Login.")
                    except:
                        st.error("User already exists.")
                else:
                    st.warning("Enter valid details.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ৬. ট্রাস্ট ও সিকিউরিটি নোটিশ
    st.markdown("""
    <div style="background-color: #0b1329; padding: 10px; border-radius: 6px; border-left: 4px solid #10b981;">
        <p style="color: #10b981; font-size: 11px; margin: 0; font-weight: bold;">✓ Zero-Knowledge Privacy Enabled</p>
        <p style="color: #64748b; font-size: 11px; margin: 3px 0 0 0;">Your credentials are locally hashed and never stored in plain text.</p>
    </div>
    """, unsafe_allow_html=True)

# --- ৭. মেইন চ্যাট ইন্টারফেস ---
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    try:
        my_lottie_data = load_my_anim("https://lottie.host/8040d75a-5262-4217-a9a7-961453a25d2a/T87hS79p1U.json")
        if my_lottie_data:
            st_lottie(my_lottie_data, height=200, key="skin_scanner_anim")
    except:
        pass

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
    unsafe_allow_html=True)

file = st.file_uploader("Upload Skin Photo", type=["jpg", "png", "jpeg"])

# --- ইমেজ প্রসেসিং এবং রেজাল্ট ---
# --- ইমেজ প্রসেসিং এবং রেজাল্ট ---
if file:
    img_res = Image.open(file).convert('RGB').resize((100, 75))
    x = np.asarray(img_res) / 255.0
    x = np.expand_dims(x, axis=0)
    pred = model.predict(x, verbose=0)
    st.session_state.last_res = classes[np.argmax(pred)]

    # ২. ডাবল ল্যাঙ্গুয়েজ ডাটাবেস (Bangla & English)
    disease_info = {
        "Actinic keratoses": {
            "local_bn": "রোদে পোড়া খসখসে দাগ", "desc_bn": "এটি সূর্যরশ্মির কারণে হয়।",
            "local_en": "Actinic Keratosis", "desc_en": "Rough, scaly patches caused by long-term sun exposure."
        },
        "Basal cell carcinoma": {
            "local_bn": "সাধারণ স্কিন ক্যান্সার", "desc_bn": "এটি এক প্রকার স্কিন ক্যান্সার।",
            "local_en": "Basal Cell Carcinoma", "desc_en": "A type of skin cancer that begins in the basal cells."
        },
        "Benign keratosis-like lesions": {
            "local_bn": "ক্ষতিহীন আঁচিল বা তিল", "desc_bn": "এটি সাধারণত ভয়ের কিছু নয়।",
            "local_en": "Benign Keratosis", "desc_en": "Non-cancerous skin growths that appear with aging."
        },
        "Dermatofibroma": {
            "local_bn": "ত্বকের শক্ত গুটি", "desc_bn": "ত্বকের নিচে ছোট শক্ত দানা।",
            "local_en": "Dermatofibroma", "desc_en": "Common benign skin nodules that feel like small, hard bumps."
        },
        "Melanocytic nevi": {
            "local_bn": "সাধারণ তিল বা জন্মদাগ", "desc_bn": "এটি আমাদের ত্বকের অতি পরিচিত তিল।",
            "local_en": "Melanocytic Nevi (Mole)", "desc_en": "Common, benign skin growths safely known as moles."
        },
        "Melanoma": {
            "local_bn": "মারাত্মক স্কিন ক্যান্সার", "desc_bn": "এটি দ্রুত চিকিৎসা করা জরুরি।",
            "local_en": "Melanoma", "desc_en": "The most serious type of skin cancer; requires immediate medical care."
        },
        "Vascular lesions": {
            "local_bn": "রক্তনালীর লাল দাগ", "desc_bn": "জন্মগত লাল দাগ বা রক্তনালী ফুলে যাওয়া।",
            "local_en": "Vascular Lesion", "desc_en": "Skin abnormalities related to blood vessels, like birthmarks."
        }
    }
    
    res_name = st.session_state.last_res
    info = disease_info.get(res_name, {
        "local_bn": "অজানা সমস্যা", "desc_bn": "বিস্তারিত তথ্য পাওয়া যায়নি।",
        "local_en": "Unknown Condition", "desc_en": "No detailed information available."
    })

    # ৩. ইউজার চ্যাটে বা ইনপুটে বাংলা লিখছে কি না তা ট্র্যাক করা
    # ডিফল্টভাবে কার্ডটি ইংরেজিতে দেখাবে, যদি ইউজার বাংলায় কিছু না চায়
    show_english = True 

    # ল্যাঙ্গুয়েজ সিলেকশন অনুযায়ী টাইটেল ও সাবটাইটেল ডাইনামিক করা
    if show_english:
        card_title = "AI Diagnostic Analysis"
        name_label = "Common Name:"
        sci_label = "Scientific Name:"
        info_label = "Information:"
        display_name = info['local_en']
        display_desc = info['desc_en']
    else:
        card_title = "AI ডায়াগনস্টিক বিশ্লেষণ"
        name_label = "সাধারণ নাম:"
        sci_label = "বৈজ্ঞানিক নাম:"
        info_label = "তথ্য:"
        display_name = info['local_bn']
        display_desc = info['desc_bn']

    # ৪. গর্জিয়াস কার্ড ডিজাইন (সম্পূর্ণ ডাইনামিক)
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 30px; border-radius: 20px; border-left: 8px solid #58a6ff; box-shadow: 0 15px 35px rgba(0,0,0,0.5); margin: 25px 0; text-align: center;">
        <p style="color: #58a6ff; font-size: 14px; text-transform: uppercase; letter-spacing: 3px; font-weight: 700;">{card_title}</p>
        <div style="margin: 20px 0;">
            <p style="color: #8b949e; margin-bottom: 5px; font-size: 14px;">{name_label}</p>
            <h1 style="color: #ffffff; font-size: 32px; margin: 0;">{display_name}</h1>
        </div>
        <div style="margin: 20px 0; border-top: 1px solid #334155; padding-top: 15px;">
            <p style="color: #8b949e; margin-bottom: 5px; font-size: 14px;">{sci_label}</p>
            <h3 style="color: #58a6ff; font-style: italic; font-size: 22px; margin: 0;">{res_name}</h3>
        </div>
        <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-top: 20px;">
            <p style="color: #cbd5e1; font-size: 15px; line-height: 1.6; margin: 0;"><b>{info_label}</b> {display_desc}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown("---")

# --- ৩. ডক্টর কনসালটেশন পপ-আপ ফাংশন ---
@st.dialog("🩺 Professional Doctor Consultation")
def doctor_booking_popup():
    st.write("Please fill in your details to book an appointment.")

    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Patient Name", key="name_f")
        patient_age = st.number_input("Age", min_value=0, max_value=120, key="age_f")
        doctor = st.selectbox("Select Specialist", ["Dr. Sabina Yasmin (1200 BDT)", "Dr. Rayhan Ahmed (1000 BDT)"], key="doc_f")
        
    with col2:
        phone_number = st.text_input("Phone Number", key="phone_f")
        user_email = st.text_input("Gmail Address", key="email_f")
        pref_date = st.date_input("Preferred Date", key="date_f")

    # অ্যাপয়েন্টমেন্টের জন্য বাড়তি অপশন
    symptoms = st.text_area("Brief description of symptoms/issues", key="symptoms_f")
    pref_time = st.selectbox("Preferred Time Slot", ["4:00 PM - 5:00 PM", "7:00 PM - 8:00 PM"], key="time_f")
    
    st.divider()
    payment_method = st.radio("Select Payment Method", 
                             ["বিকাশ/নগদ/রকেট", "Bank Transfer", "Credit/Debit Card"], 
                             key="pay_f")
    
    st.info(f"You selected: {payment_method}. No transaction ID is required at this stage.")
    # কনফার্ম বাটন
    if st.button("Confirm Appointment", use_container_width=True, key=f"confirm_btn_{doctor}_{pref_date}_{pref_time}"):
        
        user_email_str = str(st.session_state.get('email_f', ''))
        phone_number_str = str(st.session_state.get('phone_f', ''))
        
        if not phone_number_str or not user_email_str:
            st.error("Please fill up both Phone Number and Gmail Address!")
        else:
            try:
                # ডাটাবেস অপারেশান
                conn = sqlite3.connect('skinai_wishy_v30.db', check_same_thread=False)
                c = conn.cursor()
                c.execute("INSERT INTO bookings (user_email, phone_number, doctor_name, date, time, status) VALUES (?, ?, ?, ?, ?, ?)", 
                          (user_email_str, phone_number_str, doctor, str(pref_date), pref_time, 'Confirmed'))
                conn.commit()
                conn.close()
                
                # সাকসেস মেসেজ
                st.success("Appointment successfully confirmed!")
                st.info("Booking details have been sent to your provided email and phone number.")
                st.balloons() 
                
                time.sleep(10) # ১০ সেকেন্ড বিরতি
                st.rerun()

            except Exception as e:
                # এটিই একমাত্র এবং সর্বশেষ এক্সেপশন হ্যান্ডলার
                st.error(f"An unexpected error occurred: {e}")
            # তুমি যে কোনো বাংলাদেশী গেটওয়ে থেকে API Key ও Sender ID কিনলে এই ফরম্যাটে কোড হবে:
            sms_url = "http://api.smsgateway.com/send" # গেটওয়ের API লিঙ্ক
            params = {
                "api_key": "YOUR_API_KEY",
                "phone": phone_number_str,
                "message": f"SkinAI: Your booking with {doctor} on {pref_date} is confirmed!"
            }
            # বাটন প্রেসের ভেতরে এই try-except ব্লকটি এভাবে রাখুন:
    # বাটন প্রেসের ভেতরে এই try-except ব্লকটি এভাবে রাখুন:
        
        # এখানে আপনার আগের ডাটাবেস কোড থাকবে...
        
        try:
            # ১. এসএমএস এপিআই রিকোয়েস্ট
            requests.get(sms_url, params=params)
            
            # ২. সাকসেস মেসেজ
            st.success("Appointment successfully confirmed!")
            st.info("Booking details have been sent to your provided email and phone number.")
            st.balloons() 
            
            # ৩. ১৫ সেকেন্ড বিরতি ও রিলোড
            time.sleep(15) 
            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")
        user_email_str = str(st.session_state.email_f) if 'email_f' in st.session_state else ""
        phone_number_str = str(st.session_state.phone_f) if 'phone_f' in st.session_state else ""
        doctor = st.session_state.doc_f
        pref_date = st.session_state.date_f
        pref_time = st.session_state.time_f

        import re
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        phone_pattern = r'^\+?[0-9]{11,14}$'
        
        if phone_number_str == "" or user_email_str == "":
            st.error("Please fill up both Phone Number and Gmail Address!")
        elif not re.match(email_pattern, user_email_str):
            st.error("Please enter a valid Gmail address!")
        elif not re.match(phone_pattern, phone_number_str):
            st.error("Please enter a valid 11-digit Phone Number!")
        else:
            # ১. ডাটাবেস সেভ লজিক
            conn = sqlite3.connect('skinai_wishy_v30.db', check_same_thread=False)
            c = conn.cursor()
            c.execute("INSERT INTO bookings (user_email, phone_number, doctor_name, date, time, status) VALUES (?, ?, ?, ?, ?, ?)", 
                      (user_email_str, phone_number_str, doctor, str(pref_date), pref_time, 'Confirmed'))
            conn.commit()
            conn.close()
            st.success("Appointment successfully committed!")

            # ২. ইমেইল পাঠানো
            try:
                msg = EmailMessage()
                msg['Subject'] = 'Appointment Confirmation - SkinAI'
                msg['From'] = 'your_email@gmail.com'
                msg['To'] = user_email_str
                msg.set_content(f"Dear User, your appointment with {doctor} is booked for {pref_date} at {pref_time}.")
                
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login('your_email@gmail.com', 'your_app_password')
                    smtp.send_message(msg)
                st.info("Confirmation email sent successfully.")
            except Exception as e:
                st.warning(f"Email could not be sent: {e}")
            
            time.sleep(1)
            st.rerun()

# মেইন বডিতে এই অংশটি রাখো, অন্য কোনো বাটন ডিলিট করে দাও
col1, col2, col3 = st.columns([3, 4, 3])
with col2:
    if st.button("🩺 Consult a Doctor Now", use_container_width=True, key="btn_open_popup"):
        doctor_booking_popup()

st.markdown("---")

# --- ৪. চ্যাট মেসেজ লুপ এবং ইনপুট ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): 
        st.markdown(m["content"])

if prompt := st.chat_input("Ask me anything about your skin..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    if st.session_state.get('logged_in', False):
        c.execute('INSERT INTO chat_history VALUES (?,?,?)', (st.session_state.user, "user", prompt))
        conn.commit()
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        reply = get_intelligent_response(prompt, st.session_state.last_res)
        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
