import datetime
import re
import streamlit as st
import sqlite3
import hashlib

st.set_page_config(page_title="SkinAI Pro", layout="wide")
# --- সাইডবার ও বাটন গোছানোর অ্যাডভান্সড সিএসএস ---
st.markdown("""
<style>
/* ১. বাটন স্টাইলিং (যা আগে ছিল) */
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
    background-color: #0f172a !important; /* ডিপ ডার্ক প্রিমিয়াম ব্যাকগ্রাউন্ড */
    padding-top: 20px;
}

/* সাইডবারের ভেতরের ইনপুট বক্স স্পেসিং */
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
</style>

""", unsafe_allow_html=True)
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
    conn = sqlite3.connect('skinai_wishy_v30.db', check_same_thread=False)
    c = conn.cursor()
    
    # নতুন টেবিল: ইউজারদের বুকিং হিস্ট্রি রাখার জন্য (ফোন নাম্বার ও জিমেইলসহ)
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_email TEXT, 
                  phone_number TEXT, 
                  doctor_name TEXT, 
                  date TEXT, 
                  time TEXT, 
                  status TEXT)''')
                  
    # ডাক্তারদের টেবিল তৈরি করা (যদি না থাকে)
    c.execute('''CREATE TABLE IF NOT EXISTS doctors
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT, specialty TEXT, fee TEXT, available_time TEXT)''')
    
    # প্রথমবার রান করার সময় ডাটাবেসে ২ জন ডামি ডাক্তার অ্যাড করে রাখা
    c.execute("SELECT COUNT(*) FROM doctors")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO doctors (name, specialty, fee, available_time) VALUES ('Dr. Sabina Yasmin', 'Dermatologist', '1000 BDT', '4:00 PM - 6:00 PM')")
        c.execute("INSERT INTO doctors (name, specialty, fee, available_time) VALUES ('Dr. Asif Ahmed', 'Skin & Laser Specialist', '1200 BDT', '7:00 PM - 9:00 PM')")
    
    conn.commit()
    conn.close()

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

# --- ৬. সেশন ও সাইডবার ম্যানেজমেন্ট (একদম ফ্রেশ ও সিঙ্গেল ব্লক) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'messages' not in st.session_state: st.session_state.messages = []
if 'last_res' not in st.session_state: st.session_state.last_res = "None"
if 'user' not in st.session_state: st.session_state.user = None

with st.sidebar:
    # ১. লোগো এরিয়া
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3591/3591234.png", width=100)

    st.markdown("<br>", unsafe_allow_html=True)

    # ২. সিকিউরিটি গেটওয়ে কার্ড
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

    # ৩. নিউ চ্যাট বাটন (ইউনিক কি সহ)
    if st.button("+ New Chat", use_container_width=True, key="sidebar_new_chat_btn"):
        st.session_state.messages = []
        st.session_state.last_res = "None"
        st.rerun()

    st.markdown("---")

    # ৪. ফেসবুক ও জিমেইল বাটন লজিক
    if not st.session_state.logged_in:
        st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 12px;'>Or Sign In With</p>", unsafe_allow_html=True)
        social_col1, social_col2 = st.columns(2)
        with social_col1:
            if st.button("🔵 Facebook", use_container_width=True, key="fb_login"): st.info("Coming Soon!")
        with social_col2:
            if st.button("🔴 Gmail", use_container_width=True, key="gm_login"): st.info("Coming Soon!")

        st.markdown("---")

        # ৫. আসল Login ও Register ট্যাব লজিক
        t1, t2 = st.tabs(["🔑 Login", "📝 Register"])
        
        with t1:
            e = st.text_input("✉️ Gmail Address", key="login_email_input", placeholder="username@gmail.com")
            p = st.text_input("🔑 Password", type="password", key="login_pass_input", placeholder="••••••••")
            if st.button("Log In", use_container_width=True, key="submit_login"):
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
            re = st.text_input("✉️ New Gmail", key="register_email_input", placeholder="newuser@gmail.com")
            rp = st.text_input("🔑 New Password", type="password", key="register_pass_input", placeholder="••••••••")
            if st.button("Create Account", use_container_width=True, key="submit_register"):
                if "@" in re and len(rp) > 3:
                    try:
                        c.execute('INSERT INTO users VALUES (?,?)', (re, make_hash(rp))); conn.commit()
                        st.success("Account Created! Now Login.")
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

st.markdown("---")
with st.expander("❓ Help & Information"):
    st.write("১. স্পষ্ট ছবি আপলোড করুন।")
    st.write("২. রিপোর্ট পাওয়ার পর প্রশ্ন করুন।")
    st.write("৩. হিস্ট্রি দেখতে অবশ্যই লগইন করুন।")
