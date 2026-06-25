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
    
    # 🩺 নতুন টেবিল: ডাক্তারদের লিস্ট রাখার জন্য
    c.execute('''CREATE TABLE IF NOT EXISTS doctors 
                 (id INTEGER PRIMARY KEY, name TEXT, specialty TEXT, fee TEXT, available_time TEXT)''')
    
    # 🗓️ নতুন টেবিল: ইউজারদের বুকিং হিস্ট্রি রাখার জন্য
    c.execute('''CREATE TABLE IF NOT EXISTS bookings 
                 (id INTEGER PRIMARY KEY, user_email TEXT, doctor_name TEXT, date TEXT, time TEXT, status TEXT)''')
    
    # প্রথমবার রান করার সময় ডাটাবেসে ২ জন ডামি ডাক্তার অ্যাড করে রাখা
    c.execute("SELECT COUNT(*) FROM doctors")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO doctors (name, specialty, fee, available_time) VALUES ('Dr. Sabina Yasmin', 'Dermatologist', '1000 BDT', '4:00 PM - 6:00 PM')")
        c.execute("INSERT INTO doctors (name, specialty, fee, available_time) VALUES ('Dr. Asif Ahmed', 'Skin & Laser Specialist', '1200 BDT', '7:00 PM - 9:00 PM')")
        
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
        'cause': "বয়স বৃদ্ধি এবং কিছুটা জীনগত কারণ।",'home': "নারিকেল তেল বা ময়েশ্চারাইজার লাগাতে পারেন যদি চুলকানি হয়।",
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
    unsafe_allow_html=True)
file = st.file_uploader("Upload Skin Photo", type=["jpg", "png", "jpeg"])

# --- ইমেজ প্রসেসিং এবং রেজাল্ট ---
if file:
    import numpy as np
    img_res = Image.open(file).convert('RGB').resize((100, 75))
    x = np.asarray(img_res) / 255.0
    x = np.expand_dims(x, axis=0)
    pred = model.predict(x, verbose=0)
    st.session_state.last_res = classes[np.argmax(pred)]

    # ২. নামের লিস্ট (মানুষ যেভাবে চেনে বনাম বৈজ্ঞানিক নাম)
    disease_info = {
        "Actinic keratoses": {"local": "রোদে পোড়া খসখসে দাগ", "desc": "এটি সূর্যরশ্মির কারণে হয়।"},
        "Basal cell carcinoma": {"local": "সাধারণ স্কিন ক্যান্সার", "desc": "এটি এক প্রকার স্কিন ক্যান্সার।"},
        "Benign keratosis-like lesions": {"local": "ক্ষতিহীন আঁচিল বা তিল", "desc": "এটি সাধারণত ভয়ের কিছু নয়।"},
        "Dermatofibroma": {"local": "ত্বকের শক্ত গুটি", "desc": "ত্বকের নিচে ছোট শক্ত দানা।"},
        "Melanocytic nevi": {"local": "সাধারণ তিল বা জন্মদাগ", "desc": "এটি আমাদের ত্বকের অতি পরিচিত তিল।"},
        "Melanoma": {"local": "মারাত্মক স্কিন ক্যান্সার", "desc": "এটি দ্রুত চিকিৎসা করা জরুরি।"},
        "Vascular lesions": {"local": "রক্তনালীর লাল দাগ", "desc": "জন্মগত লাল দাগ বা রক্তনালী ফুলে যাওয়া।"}
    }
    
    res_name = st.session_state.last_res
    info = disease_info.get(res_name, {"local": "অজানা সমস্যা", "desc": "বিস্তারিত তথ্য পাওয়া যায়নি।"})

    # ৩. তোমার নতুন রেজাল্ট কার্ড ডিজাইন
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 30px; border-radius: 20px; border-left: 8px solid #58a6ff; box-shadow: 0 15px 35px rgba(0,0,0,0.5); margin: 25px 0; text-align: center;">
        <p style="color: #58a6ff; font-size: 14px; text-transform: uppercase; letter-spacing: 3px; font-weight: 700;">AI Diagnostic Analysis</p>
        <div style="margin: 20px 0;">
            <h4 style="color: #8b949e; margin-bottom: 5px; font-size: 16px;">সাধারণ নাম:</h4>
            <h1 style="color: #ffffff; font-size: 32px; margin: 0;">{info['local']}</h1>
        </div>
        <div style="margin: 20px 0; border-top: 1px solid #334155; padding-top: 15px;">
            <p style="color: #8b949e; margin-bottom: 5px; font-size: 14px;">বৈজ্ঞানিক নাম:</p>
            <h3 style="color: #58a6ff; font-style: italic; font-size: 22px; margin: 0;">{res_name}</h3>
        </div>
        <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-top: 20px;">
            <p style="color: #cbd5e1; font-size: 15px; line-height: 1.6; margin: 0;"><b>তথ্য:</b> {info['desc']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
  # --- গর্জিয়াস রেজাল্ট ডিজাইন শেষ ---

st.markdown("---")

# --- ৩. ডক্টর কনসালটেশন পপ-আপ ফাংশন ---
@st.dialog("🩺 Professional Doctor Consultation")
def doctor_booking_popup():
    st.markdown("### Choose a Specialist & Book Your Appointment")
    
    # ডাটাবেস থেকে ডাক্তারদের লিস্ট রিড করা
    c.execute("SELECT name, specialty, fee, available_time FROM doctors")
    doctor_list = c.fetchall()

    if doctor_list:
        for doc in doctor_list:
            st.markdown(f"""
            <div style="background-color: #1e1e1e; padding: 12px; border-radius: 8px; border: 1px solid #58a6ff; margin-bottom: 10px;">
                <h4 style="color: #58a6ff; margin: 0;">{doc[0]}</h4>
                <p style="margin: 3px 0; font-size: 13px; color: #cccccc;"><b>Specialty:</b> {doc[1]} | <b>Fee:</b> {doc[2]}</p>
                <p style="margin: 3px 0; font-size: 12px; color: #ff7b72;">⏰ {doc[3]}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    
    # বুকিং ফর্ম (পপ-আপের ভেতরে)
    with st.form(key="popup_booking_form_final"):
        doc_names = [doc[0] for doc in doctor_list] if doctor_list else ["No Doctors Available"]
        selected_doc = st.selectbox("Select Specialist", doc_names)
        appointment_date = st.date_input("Preferred Date")
        appointment_time = st.selectbox("Preferred Time Slot", ["4:00 PM - 5:00 PM", "5:00 PM - 6:00 PM", "7:00 PM - 8:00 PM", "8:00 PM - 9:00 PM"])
        payment_method = st.radio("Payment Gateway", ["Pay at Chamber", "bKash / Nagad"], horizontal=True)
        
        submit_booking = st.form_submit_button("Confirm Appointment")

    if submit_booking and doctor_list:
        user_email = st.session_state.get('user', 'Guest User')
        c.execute("INSERT INTO bookings (user_email, doctor_name, date, time, status) VALUES (?, ?, ?, ?, ?)",
                  (user_email, selected_doc, str(appointment_date), appointment_time, "Confirmed"))
        conn.commit()
        st.success(f"🎉 Appointment confirmed with {selected_doc}!")
        st.rerun()

# 🎯 মেইন স্ক্রিনে শুধু এই ২য় অপশনটি (বাটন) থাকবে, ১ম অপশনের সব কার্ড-ফর্ম ডিলিট করা হয়েছে
col1, col2, col3 = st.columns([3, 4, 3])
with col2:
    if st.button("🩺 Consult a Doctor Now", use_container_width=True):
        doctor_booking_popup()

st.markdown("---")

# --- ৪. চ্যাট মেসেজ লুপ এবং ইনপুট (আগের মেইন কোড - সম্পূর্ণ নিরাপদ) ---
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
