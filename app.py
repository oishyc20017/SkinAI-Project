
import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import random
import re

# ১. পেজ ডিজাইন ও মডার্ন লুক
st.set_page_config(page_title="SkinAI Pro - Wishy", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #333; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .developer-box {
        padding: 20px; border-radius: 10px;
        background: linear-gradient(145deg, #1e2227, #2d333b);
        text-align: center; color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# ২. সাইডবার (আপনার নাম Wishy Chakma)
st.sidebar.markdown(f"""
    <div class="developer-box">
        <h2 style="color: #58a6ff;">👨‍💻 Developer</h2>
        <hr style="border: 0.5px solid #30363d;">
        <p style="font-size: 22px;"><b>Wishy Chakma</b></p>
        <p style="font-size: 14px; color: #8b949e;">Skin Disease Detection System</p>
    </div>
    """, unsafe_allow_html=True)

# ৩. স্মার্ট ল্যাঙ্গুয়েজ ও প্রফেশনাল রেসপন্স ফাংশন
def get_natural_response(user_query, condition):
    q = user_query.lower()
    
    # ভাষা শনাক্তকরণ (বাংলা/বাংলিশ কি না চেক করা)
    is_bengali = bool(re.search('[\u0980-\u09FF]', q)) or any(word in q for word in ["ki", "korbo", "osud", "bhalo", "hobe", "ji", "ha"])

    # ডাক্তারের বিষয়ে প্রশ্ন
    if any(word in q for word in ["doctor", "specialist", "ডাক্তার", "dekhabo", "hospital"]):
        if is_bengali:
            return f"আপনার {condition}-এর জন্য একজন ডার্মাটোলজিস্ট (চর্মরোগ বিশেষজ্ঞ) দেখানো সবচেয়ে ভালো হবে। আপনি কি কোনো পরামর্শ চাচ্ছেন?"
        else:
            return f"For your diagnosed {condition}, I recommend consulting a Dermatologist for a professional checkup."

    # ঔষধ বা ক্রিম নিয়ে প্রশ্ন
    elif any(word in q for word in ["medicine", "cream", "ঔষধ", "osud", "lagabo"]):
        if is_bengali:
            return f"⚠️ **সতর্কতা:** {condition}-এর ওপর ডাক্তারের পরামর্শ ছাড়া কোনো ক্রিম বা ঔষধ লাগাবেন না।"
        else:
            return f"⚠️ **Warning:** Please do not apply any medicine for {condition} without a doctor's prescription."

    # যত্ন বা করণীয় (এবং সাধারণ উত্তর যেমন 'yes', 'ji', 'ji')
    elif any(word in q for word in ["care", "tips", "যত্ন", "what to do", "yes", "ji", "ha", "ji"]):
        if is_bengali:
            return f"✅ **পরামর্শ:** আক্রান্ত জায়গাটি পরিষ্কার রাখুন, ঘষাঘষি করবেন না এবং সরাসরি রোদ এড়িয়ে চলুন।"
        else:
            return f"✅ **Advice:** Keep the area clean, avoid scratching, and stay protected from direct sunlight."

    # ডিফল্ট উত্তর
    else:
        if is_bengali:
            return f"আপনার {condition} সম্পর্কে আমি আরও কীভাবে সাহায্য করতে পারি? আপনি যত্ন বা ডাক্তারের বিষয়ে প্রশ্ন করতে পারেন।"
        else:
            return f"I can help you with more info on {condition}. Would you like to know about care tips or doctor recommendations?"

# ৪. মডেল লোড ও মেইন অ্যাপ ইন্টারফেস
@st.cache_resource
def load_my_model():
    return tf.keras.models.load_model('skin_cancer_model.h5', compile=False)

model = load_my_model()
classes = ['Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis', 'Dermatofibroma', 'Melanoma', 'Nevus', 'Vascular lesions']

st.title("🩺 SkinAI Professional Assistant")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📸 Upload Skin Image")
    file = st.file_uploader("", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file).convert('RGB')
        st.image(img, use_container_width=True)

with col2:
    if file:
        img_res = img.resize((100, 75))
        x = np.asarray(img_res) / 255.0
        x = np.expand_dims(x, axis=0)
        pred = model.predict(x, verbose=0)
        result = classes[np.argmax(pred)]
        
        st.success(f"### Detection Result: {result}")
        st.markdown("---")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        chat_container = st.container(height=400)
        with chat_container:
            for m in st.session_state.messages:
                with st.chat_message(m["role"], avatar="👨‍💻" if m["role"] == "user" else "🤖"):
                    st.markdown(m["content"])

        if prompt := st.chat_input("বাংলা বা English-এ প্রশ্ন করুন..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user", avatar="👨‍💻"): st.markdown(prompt)
                with st.chat_message("assistant", avatar="🤖"):
                    reply = get_natural_response(prompt, result)
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
