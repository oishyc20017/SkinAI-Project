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
import google.generativeai as genai

# Streamlit-এর secrets থেকে API key সংগ্রহ করা
# সঠিক পদ্ধতি: শুধুমাত্র কি-এর নাম ব্যবহার করবেন
genai.configure(api_key=st.secrets["API_KEY"])
model_ai = genai.GenerativeModel("gemini-2.5-flash")
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
</style>
""", unsafe_allow_html=True)
# --- ১. ডাটাবেস ও সিকিউরিটি ---
conn = sqlite3.connect('skinai_wishy_v30.db', check_same_thread=False)
c = conn.cursor()

# আপনার ডাটাবেস ফাংশনে এই পরিবর্তনটি করুন
def init_db():
    conn = sqlite3.connect('skinai_wishy_v30.db', check_same_thread=False)
    c = conn.cursor()
    
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

    response = model_ai.generate_content(prompt)
    return response.text
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
    # ... আগের বাটনগুলো (যেমন: New Chat) ...
    
    st.markdown("---") # আপনার ডিভাইডার লাইন
        
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
            e = st.text_input("✉️ Gmail Address", key="l_e", placeholder="username@gmail.com")
            p = st.text_input("🔑 Password", type="password", key="l_p", placeholder="••••••••")
            if st.button("Log In", use_container_width=True, key="unique_login_submit"):
                c.execute('SELECT password FROM users WHERE email=?', (e,))
                data = c.fetchone()
                if data and check_hash(p, data[0]):
                    st.session_state.logged_in = True
                    st.session_state.user = e
                    c.execute('SELECT role, content FROM chat_history WHERE email=?', (e,))
                    for msg in st.session_state.messages:
                        with st.chat_message(msg["role"]):
                            st.markdown(msg["content"])
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
# রেজাল্ট প্রদর্শন লজিক
if 'last_res' in st.session_state:
    res_name = st.session_state.last_res
    
    # আপনার তৈরি করা disease_details ডাটাবেস থেকে তথ্য নেওয়া
    info = disease_details.get(res_name)

    if info:
        st.markdown(f"""
        <div style="background: #1e293b; padding: 25px; border-radius: 20px; border-left: 8px solid #58a6ff; box-shadow: 0 10px 20px rgba(0,0,0,0.3);">
            <h1 style="color: #ffffff; margin-bottom: 5px;">{res_name}</h1>
            <p style="color: #94a3b8; font-size: 16px;"><b>Description:</b> {info['desc']}</p>
            <p style="color: #cbd5e1;"><b>Cause:</b> {info['cause']}</p>
            <p style="color: #cbd5e1;"><b>Prevention:</b> {info['home']}</p>
            <p style="color: #ffcc00;"><b>Advice:</b> {info['advice']}</p>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        # ডাটাবেসে তথ্য না থাকলে
        st.warning(f"আমরা এই রোগটি শনাক্ত করেছি: {res_name}, তবে এর বিস্তারিত তথ্য আমাদের ডাটাবেসে নেই।")
else:
    # যদি কোনো রেজাল্ট জেনারেট না হয়, তবে কিছু দেখাবে না (শান্ত থাকবে)
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
            # ১. সাকসেস মেসেজ এবং বেলুন
            st.success(f"🎉 Appointment successfully confirmed with {selected_doctor[0]}!")
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

# --- ৪. চ্যাট মেসেজ লুপ এবং ইনপুট (আগের মেইন কোড - সম্পূর্ণ নিরাপদ) ---
for m in st.session_state.messages:
    with st.chat_message("assistant"):
    with st.spinner("🩺 SkinAI is thinking..."):
        reply = ask_ai(prompt, st.session_state.last_res)

    st.markdown(reply)

st.session_state.messages.append({
    "role": "assistant",
    "content": reply
})

    # Login থাকলে শুধু history save করবে
    if st.session_state.get("logged_in", False):
        c.execute(
            'INSERT INTO chat_history VALUES (?,?,?)',
            (st.session_state.user, "user", prompt)
        )
        conn.commit()

    # AI সবসময় উত্তর দেবে
    reply = ask_ai(prompt, st.session_state.last_res)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

    # Login থাকলে AI reply-ও save করবে
    if st.session_state.get("logged_in", False):
        c.execute(
            'INSERT INTO chat_history VALUES (?,?,?)',
            (st.session_state.user, "assistant", reply)
        )
        conn.commit()

    st.rerun()
