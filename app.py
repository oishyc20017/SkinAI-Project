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
import streamlit as st
from streamlit_option_menu import option_menu
import sqlite3
import time
import secrets
import google.generativeai as genai
from requests_oauthlib import OAuth2Session


# ---------------- CONFIG ----------------
genai.configure(api_key=st.secrets["API_KEY"])
model_ai = genai.GenerativeModel("gemini-2.5-flash")


GOOGLE_CLIENT_ID = st.secrets["CLIENT_ID"]
GOOGLE_CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]

AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"

SCOPES = ["openid", "email", "profile"]

# ---------------- CALLBACK ----------------
def google_callback():

    params = st.query_params

    if "code" not in params:
        return

    try:
        client = OAuth2Session(
            GOOGLE_CLIENT_ID,
            redirect_uri=REDIRECT_URI,
            state=st.session_state.get("oauth_state")
        )

        token = client.fetch_token(
            TOKEN_ENDPOINT,
            code=params["code"],
            client_secret=GOOGLE_CLIENT_SECRET
        )

        resp = client.get(USERINFO_ENDPOINT)
        user = resp.json()

        email = user["email"]
        fullname = user["name"]

        conn = sqlite3.connect("skinai_wishy_v30.db", check_same_thread=False)
        c = conn.cursor()

        c.execute("SELECT fullname FROM users WHERE email=?", (email,))
        data = c.fetchone()

        if data is None:
            username = email.split("@")[0]
            random_password = secrets.token_hex(16)

            c.execute("""
                INSERT INTO users
                (fullname,username,email,phone,dob,gender,country,password)
                VALUES(?,?,?,?,?,?,?,?)
            """, (
                fullname,
                username,
                email,
                "", "", "", "",
                random_password
            ))

            conn.commit()

        st.session_state.logged_in = True
        st.session_state.user = email
        st.session_state.fullname = fullname

        conn.close()

        st.query_params.clear()

        st.success("Google Login Successful")
        time.sleep(1)
        st.rerun()

    except Exception as e:
        st.error(e)

# ---------------- LOGIN ----------------
def google_login():
    google = OAuth2Session(
        GOOGLE_CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES
    )

    authorization_url, state = google.authorization_url(
        AUTHORIZATION_ENDPOINT
    )

    st.session_state.oauth_state = state

    return authorization_url
    import streamlit.components.v1 as components

    components.html(
        f"""
        <script>
            window.top.location.href = "{authorization_url}";
        </script>
        """,
        height=0,
    )
    def main():
        google_callback()


    # ---------------- RUN ----------------
    if __name__ == "__main__":
        main()


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

    @keyframes rainbow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .user-box{
    background: linear-gradient(135deg,#2563eb,#1d4ed8);
    color:white;
    padding:14px 18px;
    border-radius:20px;
    margin:8px 0;
    width:fit-content;
    max-width:75%;
    margin-left:auto;
    box-shadow:0 5px 15px rgba(0,0,0,.25);
}

.ai-box{
    background:#1e293b;
    color:white;
    padding:14px 18px;
    border-radius:20px;
    margin:8px 0;
    width:fit-content;
    max-width:75%;
    border:1px solid #334155;
    box-shadow:0 5px 15px rgba(0,0,0,.25);
}

.chat-name{
    font-size:13px;
    font-weight:600;
    margin-bottom:6px;
    opacity:.8;
}
        /* Recent Chats Button */
        div.stButton > button {
            border-radius: 10px !important;
            text-align: left !important;
            justify-content: flex-start !important;
            padding: 8px 12px !important;
        }
                /* New Chat Button */
                div[data-testid="stButton"] button {
                    border-radius: 10px;
                    padding: 7px 10px;
                    font-size: 14px;
                }
    

</style>
""", unsafe_allow_html=True)
# --- ১. ডাটাবেস ও সিকিউরিটি ---
conn = sqlite3.connect('skinai_wishy_v30.db', check_same_thread=False)
c = conn.cursor()

# আপনার ডাটাবেস ফাংশনে এই পরিবর্তনটি করুন
def init_db():
    conn = sqlite3.connect('skinai_wishy_v30.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        dob TEXT,
        gender TEXT,
        country TEXT,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # ---------- Conversations Table ----------
    c.execute("""
    CREATE TABLE IF NOT EXISTS conversations(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        title TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # ---------- Messages Table ----------
    c.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER,
        role TEXT,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(conversation_id) REFERENCES conversations(id)
    )
    """)
    
    # ডাক্তারদের টেবিল ড্রপ করে নতুন করে তৈরি করুন (যাতে পুরনো ভুল ডাটা মুছে যায়)
    c.execute('DROP TABLE IF EXISTS doctors')
    c.execute('''CREATE TABLE IF NOT EXISTS doctors
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT, specialty TEXT, fee TEXT, available_time TEXT, hospital_name TEXT)''')
                  
    # একাধিক ডাক্তার যোগ করার তালিকা
    doctors_list = [
        ('Dr. Sabina Yasmin', 'Dermatologist', '1000 BDT', '4:00 PM - 6:00 PM', 'Dhaka Medical Center'),
        ('Dr. Asif Ahmed', 'Skin & Laser Specialist', '1200 BDT', '7:00 PM - 9:00 PM', 'City Skin Hospital'),
        ('Dr. Farhana Begum', 'Dermatologist', '1500 BDT', '10:00 AM - 12:00 PM', 'Apollo Skin Clinic'),
        ('Dr. M. Rahman', 'Cosmetic Dermatologist', '1100 BDT', '2:00 PM - 4:00 PM', 'Square Hospital'),
        ('Dr. Tasnim Kabir', 'Skin Specialist', '900 BDT', '6:00 PM - 8:00 PM', 'Popular Medical')
    ]
    
    # একসাথে সব ডাটা ইনসার্ট করা
    c.executemany("INSERT INTO doctors (name, specialty, fee, available_time, hospital_name) VALUES (?, ?, ?, ?, ?)", doctors_list)
    # ---------- Bookings Table ----------
    c.execute("DROP TABLE IF EXISTS bookings")
    c.execute("""
    CREATE TABLE IF NOT EXISTS bookings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id TEXT UNIQUE,
        patient_name TEXT NOT NULL,
        user_email TEXT NOT NULL,
        phone_number TEXT,
        age INTEGER,
        doctor_name TEXT NOT NULL,
        specialty TEXT,
        hospital_name TEXT,
        booking_date TEXT,
        booking_time TEXT,
        symptoms TEXT,
        payment_method TEXT,
        status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

init_db()

def make_hash(p): return hashlib.sha256(str.encode(p)).hexdigest()
def check_hash(p, h): return h if make_hash(p) == h else False

# --- ৪. ইন্টেলিজেন্ট ল্যাঙ্গুয়েজ সুইচ ইঞ্জিন (Fix: English vs Bangla/Banglish) ---
def ask_ai(user_question, disease):

    prompt = f"""
You are SkinAI Pro, a friendly and experienced virtual dermatologist.

The detected skin disease from the uploaded image is:
{disease}

Instructions:
- Reply naturally like a human dermatologist.
- Be friendly, clear, and professional.
- Answer ONLY the user's question.
- Do NOT always explain the disease automatically.
- If the user only says "hi", "hello", or greets you, greet back and ask how you can help.
- Only discuss the detected disease if the user asks about it.
- If the question is in Bangla or Banglish, reply in Bangla.
- If the question is in English, reply in English.
- If you don't know something, say so instead of making it up.
- Give only safe medical advice.
- Never claim a diagnosis is certain from a photo.
- Treat Banglish (Bangla written in English letters) as Bangla and reply in natural Bangla.
- Understand common Banglish spellings even if they are not perfectly spelled.

If the user's question is related to the detected disease, answer based on that disease.

If the question is unrelated (for example: "How are you?", "Who are you?", "Tell me a joke"), answer normally without mentioning the disease.

Never force the disease into every reply.

User Question:
{user_question}
"""
    try:
        response = model_ai.generate_content(prompt)
        return response.text

    except Exception as e:
        error = str(e)

        if "ResourceExhausted" in error or "429" in error:
            return "⚠️ AI request limit has been reached. Please try again later."

        return "⚠️ SkinAI is temporarily unavailable. Please try again in a few moments."
# --- ৫. মডেল লোডিং ---
@st.cache_resource
def load_skin_model():
    path = 'skin_cancer_model.h5'
    if not os.path.exists(path): gdown.download(id='1JpKXUXu_DsXK5-uq7fpgg5aDY7hBhq9h', output=path, quiet=False)
    return tf.keras.models.load_model(path, compile=False)
model = load_skin_model()
disease_details = {
    'Actinic keratoses': {
        'desc': 'A rough, scaly patch on the skin caused by years of sun exposure.',
        'cause': 'Long-term exposure to ultraviolet (UV) radiation from the sun.',
        'home': 'Use sunscreen daily, avoid peak sun hours, and keep skin moisturized.',
        'advice': 'Consult a dermatologist to ensure it is not pre-cancerous.'
    },
    'Basal cell carcinoma': {
        'desc': 'A common type of skin cancer that begins in the basal cells.',
        'cause': 'Prolonged exposure to sunlight or UV rays.',
        'home': 'No home remedy; regular skin protection is essential.',
        'advice': 'Requires professional treatment or biopsy; see a doctor immediately.'
    },
    'Benign keratosis': {
        'desc': 'Non-cancerous skin growth, often appearing as a dark or tan spot as you age.',
        'cause': 'Natural aging process and genetics.',
        'home': 'Keep it moisturized; coconut oil may help if there is mild itching.',
        'advice': 'Usually no treatment needed, but see a doctor if it grows rapidly.'
    },
    'Dermatofibroma': {
        'desc': 'A small, firm red or brown bump, often on the legs or arms.',
        'cause': 'Usually a reaction to a minor injury like an insect bite.',
        'home': 'No specific home treatment.',
        'advice': 'If it becomes painful or changes in appearance, consult a doctor for removal.'
    },
    'Melanoma': {
        'desc': 'The most serious type of skin cancer that can spread rapidly.',
        'cause': 'Genetic mutations and intense UV exposure.',
        'home': 'No home treatment; this is a medical emergency.',
        'advice': 'Urgent consultation with an oncologist or dermatologist is mandatory.'
    },
    'Nevus': {
        'desc': 'A common mole; a cluster of pigmented skin cells.',
        'cause': 'Concentration of melanin cells.',
        'home': 'Sun protection to prevent irritation.',
        'advice': 'Monitor for changes in size, shape, or color; see a doctor if it changes.'
    },
    'Vascular lesions': {
        'desc': 'Skin conditions caused by abnormal blood vessels (red or purple spots).',
        'cause': 'Blood vessel malformations.',
        'home': 'Ice packs may reduce swelling, but it is not a permanent solution.',
        'advice': 'Laser treatment is usually recommended for complete removal.'
    }
}
classes = list(disease_details.keys())

# --- ৬. সেশন ও সাইডবার ম্যানেজমেন্ট (Buttons & History Fixed) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_titles" not in st.session_state:
    st.session_state.chat_titles = []

if "last_res" not in st.session_state:
    st.session_state.last_res = None

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

if "confidence" not in st.session_state:
    st.session_state.confidence = 0.0

if "predictions" not in st.session_state:
    st.session_state.predictions = []

if "oauth_state" not in st.session_state:
    st.session_state.oauth_state = None
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "google_user" not in st.session_state:
    st.session_state.google_user = None

google_callback()

with st.sidebar:
    # ১. লোগো এরিয়া
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3591/3591234.png", width=100)

    st.markdown("<br>", unsafe_allow_html=True)
    # ... আগের বাটনগুলো (যেমন: New Chat) ...
    
    st.markdown("---") # আপনার ডিভাইডার লাইন
        
    # ২. সিকিউরিটি গেটওয়ে কার্ড
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%);
        padding: 12px; 
        border-radius: 10px; 
        border: 1px solid #4338ca; 
        text-align: center; 
        margin-bottom: 10px;">
        <h2 style="color: #38bdf8; margin: 0; font-size: 18px;">🔒 Secure Gateway</h2>
        <p style="color: #94a3b8; font-size: 11px; margin: 5px 0 0 0;">SHA-256 Encrypted Session</p>
    </div>
    """, unsafe_allow_html=True)
        
    st.markdown("---")
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
    # ==========================================================
    # AUTHENTICATION AREA
    # ==========================================================

    # ---------------- Conversation Loader ----------------

    if "chat_titles" not in st.session_state:
        st.session_state.chat_titles = []

    # Load all conversations
    c.execute("""
    SELECT id, title
    FROM conversations
    WHERE user_email=?
    ORDER BY id DESC
    """, (st.session_state.user,))

    st.session_state.chat_titles = c.fetchall()

    # Auto select latest conversation
    if (
        st.session_state.current_conversation_id is None
        and st.session_state.chat_titles
    ):
        st.session_state.current_conversation_id = (
            st.session_state.chat_titles[0][0]
        )

    # Load current conversation messages
    if st.session_state.current_conversation_id is not None:

        c.execute("""
        SELECT role, message
        FROM messages
        WHERE conversation_id=?
        ORDER BY id
        """, (st.session_state.current_conversation_id,))

        rows = c.fetchall()

        st.session_state.messages = [
            {
                "role": role,
                "content": message
            }
            for role, message in rows
        ]
    if st.session_state.get("logged_in", False):

        # ---------------- User Card ----------------
        st.markdown(f"""
        <div style="
            background:#1f2937;
            padding:15px;
            border-radius:12px;
            border:1px solid #374151;
            margin-bottom:15px;
        ">
            <h4 style="margin:0;color:white;">👤 {st.session_state.fullname}</h4>
            <p style="margin:4px 0 0 0;color:#9ca3af;font-size:13px;">
                {st.session_state.user}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # ---------------- New Chat ----------------
        if st.button(
            "➕ New Chat",
            use_container_width=True,
            key="sidebar_new_chat"
        ):

            # শুধু Session Reset হবে
            st.session_state.current_conversation_id = None
            st.session_state.messages = []
            st.session_state.last_res = None
            st.session_state.predictions = []
            st.session_state.confidence = 0.0
            st.session_state.uploader_key += 1

            st.rerun()
        st.markdown("---")

        # ---------------- Recent Chat ----------------
        c.execute("""
        SELECT id, title
        FROM conversations
        WHERE user_email=?
        ORDER BY id DESC
        """, (st.session_state.user,))

        st.session_state.chat_titles = c.fetchall()

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🕒 Recent Chats")
        # ---------------- Search Chats ----------------

        search_chat = st.text_input(
            "🔍 Search chats",
            placeholder="Type to search...",
            key="search_chat"
        )

        if len(st.session_state.chat_titles) == 0:

            st.caption("No previous chats")

        else:

            chat_labels = []
            chat_map = {}

            for chat_id, title in st.session_state.chat_titles:
                    # Search Filter
                    if search_chat:
                        if search_chat.lower() not in title.lower():
                            continue

                    if len(title) > 30:
                        title = title[:30] + "..."

                    chat_labels.append(title)
                    chat_map[title] = chat_id

            selected = option_menu(
                menu_title=None,
                options=chat_labels,
                icons=["chat-left-text"] * len(chat_labels),
                default_index=0,
                styles={
                    "container": {
                        "padding": "0!important",
                        "background-color": "transparent",
                    },
                    "icon": {
                        "color": "#60a5fa",
                        "font-size": "13px",
                    },
                    "nav-link": {
                        "font-size": "12px",
                        "text-align": "left",
                        "margin": "0px",
                        "border-radius": "6px",
                        "padding": "5px 7px",
                        "--hover-color": "#2d2d2d",
                    },
                    "nav-link-selected": {
                        "background-color": "#1f2937",
                        "color": "white",
                    },
                },
            )
                    

            if selected:

                selected_id = chat_map[selected]

                if selected_id != st.session_state.current_conversation_id:

                    st.session_state.current_conversation_id = selected_id

                    c.execute("""
                        SELECT role, message
                        FROM messages
                        WHERE conversation_id=?
                        ORDER BY id
                    """, (selected_id,))

                    rows = c.fetchall()

                    st.session_state.messages = [
                        {
                            "role": role,
                            "content": message
                        }
                        for role, message in rows
                    ]

                    st.rerun()
                    
        st.markdown("---")
        # ==========================
        # ADMIN DASHBOARD
        # ==========================
        if (
            st.session_state.get("logged_in", False)
            and st.session_state.user == "oishyc89@gmail.com"
        ):

            st.markdown("---")
            st.subheader("📊 Admin Dashboard")
            # Total Users
            c.execute("SELECT COUNT(*) FROM users")
            total_users = c.fetchone()[0]

            # Total Conversations
            c.execute("SELECT COUNT(*) FROM conversations")
            total_conversations = c.fetchone()[0]

            # Total Messages
            c.execute("SELECT COUNT(*) FROM messages")
            total_messages = c.fetchone()[0]

            # Total Bookings
            c.execute("SELECT COUNT(*) FROM bookings")
            total_bookings = c.fetchone()[0]

            st.metric("👤 Registered Users", total_users)
            st.metric("💬 Conversations", total_conversations)
            st.metric("🩺 Messages", total_messages)
            st.metric("📅 Bookings", total_bookings)

        # ---------------- Logout ----------------
        if st.button(
            "🚪 Logout",
            use_container_width=True,
            key="logout_btn"
        ):

            st.session_state.clear()

            st.rerun()

    else:

        # Social Login
        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "🔵 Facebook",
                use_container_width=True
            ):
                st.info("🚧 Facebook Login Coming Soon")

        with col2:

            google_url = google_login()

            st.link_button(
                "🔴 Continue with Google",
                google_url,
                use_container_width=True
            )
        st.markdown("---")

        t1, t2 = st.tabs(["🔑 Login", "🆕 Register"])
        with t1:

            e = st.text_input(
                "✉️ Gmail Address",
                key="l_e",
                placeholder="username@gmail.com"
            )

            p = st.text_input(
                "🔑 Password",
                type="password",
                key="l_p",
                placeholder="••••••••"
            )

            if st.button(
                "Log In",
                use_container_width=True,
                key="unique_login_submit"
            ):

                c.execute("""
                    SELECT fullname, username, password
                    FROM users
                    WHERE email=?
                """, (e,))

                data = c.fetchone()

                if data and check_hash(p, data[2]):

                    st.session_state.logged_in = True
                    st.session_state.user = e
                    st.session_state.fullname = data[0]
                    st.session_state.username = data[1]

                    st.success("✅ Welcome back!")

                    time.sleep(0.5)

                    st.rerun()

                else:
                    st.error("❌ Invalid Email or Password.")

        with t2:

            r_name = st.text_input(
                "👤 Full Name",
                key="r_name"
            )

            r_username = st.text_input(
                "👤 Username",
                key="r_username"
            )

            re = st.text_input(
                "📧 Email Address",
                key="r_e"
            )

            r_phone = st.text_input(
                "📱 Phone Number",
                key="r_phone"
            )

            r_dob = st.date_input(
                "🎂 Date of Birth",
                key="r_dob"
            )

            r_gender = st.selectbox(
                "⚧ Gender",
                [
                    "Male",
                    "Female",
                    "Prefer not to say"
                ],
                key="r_gender"
            )

            r_country = st.selectbox(
                "🌍 Country",
                [
                    "Bangladesh",
                    "India",
                    "Pakistan",
                    "Nepal",
                    "Bhutan",
                    "Sri Lanka",
                    "Myanmar",
                    "Other"
                ],
                key="r_country"
            )

            rp = st.text_input(
                "🔒 Password",
                type="password",
                key="r_p"
            )

            confirm_password = st.text_input(
                "🔒 Confirm Password",
                type="password",
                key="confirm_password"
            )

            agree = st.checkbox(
                "I agree to the Terms & Conditions"
            )

            remember = st.checkbox(
                "Remember me on this device",
                key="remember_me"
            )

            st.markdown("---")

            if st.button(
                "Create Account",
                use_container_width=True,
                key="unique_reg_submit"
            ):

                if not agree:
                    st.warning("Please accept the Terms & Conditions.")

                elif r_name.strip() == "":
                    st.warning("Please enter your Full Name.")

                elif r_username.strip() == "":
                    st.warning("Please enter a Username.")

                elif "@" not in re:
                    st.warning("Please enter a valid Email Address.")

                elif len(r_phone) < 11:
                    st.warning("Please enter a valid Phone Number.")

                elif len(rp) < 6:
                    st.warning("Password must be at least 6 characters.")

                elif rp != confirm_password:
                    st.error("Passwords do not match!")

                else:

                    try:

                        c.execute("""
                            INSERT INTO users
                            (fullname, username, email, phone, dob, gender, country, password)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            r_name,
                            r_username,
                            re,
                            r_phone,
                            str(r_dob),
                            r_gender,
                            r_country,
                            make_hash(rp)
                        ))

                        conn.commit()

                        st.success("🎉 Account Created Successfully!")
                        st.info("You can now login.")

                    except sqlite3.IntegrityError:
                        st.error("Username or Email already exists.")

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
    unsafe_allow_html=True)

# --- ইমেজ প্রসেসিং এবং রেজাল্ট ---
file = st.file_uploader(
    "Upload Skin Photo",
    type=["jpg", "png", "jpeg"],
    key=f"uploader_{st.session_state.uploader_key}"
)

if file:
    # যখন ফাইল আপলোড হবে, তখনই কেবল প্রসেসিং শুরু হবে
    img_res = Image.open(file).convert('RGB').resize((100, 75))
    x = np.asarray(img_res) / 255.0
    x = np.expand_dims(x, axis=0)
    pred = model.predict(x, verbose=0)

    # Prediction
    pred_index = np.argmax(pred)

    # Disease Name
    res_name = classes[pred_index]

    # Confidence (%)
    confidence = float(pred[0][pred_index]) * 100

    # Session
    st.session_state.last_res = res_name
    st.session_state.confidence = confidence
    st.session_state.predictions = pred[0] 

# ডাটাবেস থেকে তথ্য লোড করার অংশ (ক্লিন লজিক)
if st.session_state.last_res != "None":
    res_name = st.session_state.last_res
    info = disease_details.get(res_name)
    confidence = st.session_state.confidence

    if info:
        st.subheader("🩺 AI Skin Analysis Report")

        col1, col2 = st.columns([3, 1])

        with col1:
            st.success(f"**Detected Disease:** {res_name}")

        with col2:
            st.metric("Confidence", f"{confidence:.2f}%")

        st.progress(min(confidence / 100, 1.0))

        st.markdown("### 📋 Disease Information")

        st.info(f"**Description:** {info['desc']}")

        st.write(f"**Cause:** {info['cause']}")
        st.write(f"**Prevention:** {info['home']}")
        st.warning(f"**Advice:** {info['advice']}")

        st.error("⚠️ This AI prediction is not a confirmed medical diagnosis. Please consult a dermatologist before making any medical decision.")
        st.markdown("---")
        st.subheader("🧠 Top 3 AI Predictions")

        # সব Probability বের করা
        predictions = st.session_state.predictions

        # Probability অনুযায়ী Sort করা
        top_predictions = sorted(
            zip(classes, predictions),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        # দেখানো
        for disease, prob in top_predictions:
            percentage = prob * 100

            st.write(f"**{disease}**")
            st.progress(float(prob))
            st.caption(f"{percentage:.2f}%")

    else:
         pass
else:
            # ফাইল আপলোড না করলে একদম ক্লিন থাকবে
    pass
            # --- গর্জিয়াস রেজাল্ট ডিজাইন শেষ ---

st.markdown("---")

# --- ৩. ডক্টর কনসালটেশন পপ-আপ ফাংশন ---
@st.dialog("🩺 Professional Doctor Consultation")
def doctor_booking_popup():
    try:
        conn = sqlite3.connect('skinai_wishy_v30.db', check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT name, specialty, fee, available_time, hospital_name FROM doctors")
        doctor_list = c.fetchall()
        
        st.markdown("### Book Your Appointment")

        with st.form(key="popup_booking_form_final"):
            patient_name = st.text_input("Patient Name")
            phone_number = st.text_input("Phone Number")
            
            col1, col2 = st.columns(2)
            with col1:
                age = st.number_input("Age", min_value=0, max_value=100)
            with col2:
                gmail_address = st.text_input("Gmail Address")
            
            doctor_names = [f"{d[0]} ({d[2]})" for d in doctor_list]
            selected_name = st.selectbox("Select Specialist", doctor_names)
            selected_doctor = next(d for d in doctor_list if f"{d[0]} ({d[2]})" == selected_name)
            
            st.info(f"🏥 **Hospital:** {selected_doctor[4]} | ⏰ **Available:** {selected_doctor[3]}")
            
            preferred_date = st.date_input("Preferred Date")
            symptoms = st.text_area("Brief description of symptoms/issues")
            payment_method = st.radio("Select Payment Method", ["বিকাশ/নগদ/রকেট", "Bank Transfer", "Credit/Debit Card"])
            
            submit_button = st.form_submit_button("Confirm Appointment")

        if submit_button:
            import random

            booking_id = f"BK-{random.randint(100000,999999)}"

            c.execute("""
            INSERT INTO bookings
            (
            booking_id,
            patient_name,
            user_email,
            phone_number,
            age,
            doctor_name,
            specialty,
            hospital_name,
            booking_date,
            booking_time,
            symptoms,
            payment_method,
            status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                booking_id,
                patient_name,
                gmail_address,
                phone_number,
                age,
                selected_doctor[0],
                selected_doctor[1],
                selected_doctor[4],
                str(preferred_date),
                selected_doctor[3],
                symptoms,
                payment_method,
                "Confirmed"
            ))

            conn.commit()
            st.success("✅ Appointment Booked Successfully!")
            st.write("Booking Saved Successfully")

            c.execute("SELECT COUNT(*) FROM bookings")
            st.write("Total Bookings:", c.fetchone()[0])

            st.info(f"""
            📌 Booking ID: {booking_id}

           👤 Patient: {patient_name}

           👨‍⚕️ Doctor: {selected_doctor[0]}

           🏥 Hospital: {selected_doctor[4]}

            📅 Date: {preferred_date}

            ⏰ Time: {selected_doctor[3]}

           📌 Status: Confirmed
            """)
            st.info("Booking details have been sent to your provided email and phone number.")
            st.balloons()
            
            # ২. ১০ সেকেন্ড ওয়েট এবং রিরান
            import time
            time.sleep(10)
            st.rerun()
        
        conn.close()
    except Exception as e:
        st.error(f"Error: {e}")

# মেইন বডিতে এই অংশটি রাখো, অন্য কোনো বাটন ডিলিট করে দাও
col1, col2, col3 = st.columns([3, 4, 3])
with col2:
    if st.button("🩺 Consult a Doctor Now", use_container_width=True, key="btn_open_popup"):
        doctor_booking_popup()

st.markdown("---")

# ---------------- CHAT ----------------
if st.session_state.current_conversation_id is None:
    st.caption("No conversation selected")
for m in st.session_state.messages:

    avatar = "👤" if m["role"] == "user" else "🩺"

    name = "You" if m["role"] == "user" else "SkinAI Assistant"

    with st.chat_message(m["role"], avatar=avatar):

        st.markdown(
            f"<span style='font-size:15px;font-weight:700;'>{name}</span>",
            unsafe_allow_html=True
        )

        st.write(m["content"])
# নতুন মেসেজ
prompt = st.chat_input("Ask me anything about your skin...")


if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # ---------------- Create Conversation On First Message ----------------

    if (
        st.session_state.get("logged_in", False)
        and st.session_state.current_conversation_id is None
    ):

        c.execute("""
        INSERT INTO conversations(user_email, title)
        VALUES (?, ?)
        """, (
            st.session_state.user,
            "New Conversation"
        ))

        conn.commit()

        st.session_state.current_conversation_id = c.lastrowid
    # Login থাকলে user message save করো
    if st.session_state.get("logged_in", False):
        c.execute("""
            INSERT INTO messages (conversation_id, role, message)
            VALUES (?, ?, ?)
        """, (
            st.session_state.current_conversation_id,
            "user",
            prompt
        ))
        conn.commit()

    # AI উত্তর তৈরি
    # প্রথম Message হলে Conversation Title Update
    if st.session_state.get("logged_in", False):

        c.execute("""
        SELECT title
        FROM conversations
        WHERE id=?
        """, (st.session_state.current_conversation_id,))

        current_title = c.fetchone()

        if current_title and current_title[0] == "New Conversation":

            new_title = prompt[:40]

            c.execute("""
            UPDATE conversations
            SET title=?
            WHERE id=?
            """, (
                new_title,
                st.session_state.current_conversation_id
            ))

            conn.commit()
            # ---------------- Auto Conversation Title ----------------

            if st.session_state.get("logged_in", False):

                c.execute("""
                SELECT title
                FROM conversations
                WHERE id=?
                """, (st.session_state.current_conversation_id,))

                row = c.fetchone()

                if row and row[0] == "New Conversation":

                    title = prompt.strip()

                    if len(title) > 40:
                        title = title[:40] + "..."

                    c.execute("""
                    UPDATE conversations
                    SET title=?
                    WHERE id=?
                    """, (
                        title,
                        st.session_state.current_conversation_id
                    ))

                    conn.commit()
    with st.spinner("🩺 SkinAI is thinking..."):
        reply = ask_ai(prompt, st.session_state.last_res)

    # AI message show
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    # Login থাকলে AI message save করো
    if st.session_state.get("logged_in", False):
        c.execute("""
            INSERT INTO messages (conversation_id, role, message)
            VALUES (?, ?, ?)
        """, (
            st.session_state.current_conversation_id,
            "assistant",
            reply
        ))
        conn.commit()

    st.rerun()
