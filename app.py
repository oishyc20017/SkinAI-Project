import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
import os
import gdown
import re
import os
os.environ['GDOWN_SKIP_DOWNLOAD_ERRORS'] = '1'
# ১. পেজ সেটআপ ও ডিজাইন
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

# ২. সাইডবার (Developer: Wishy Chakma)
st.sidebar.markdown(f"""
    <div class="developer-box">
        <h2 style="color: #58a6ff;">👨‍💻 Developer</h2>
        <hr style="border: 0.5px solid #30363d;">
        <p style="font-size: 22px;"><b>Wishy Chakma</b></p>
        <p style="font-size: 14px; color: #8b949e;">Skin Disease Detection System</p>
    </div>
    """, unsafe_allow_html=True)

# ৩. স্মার্ট ল্যাঙ্গুয়েজ রেসপন্স ফাংশন
def get_natural_response(user_query, condition):
    q = user_query.lower()
    is_bengali = bool(re.search('[\u0980-\u09FF]', q)) or any(word in q for word in ["ki", "korbo", "osud", "bhalo", "hobe", "ji", "ha"])

    if any(word in q for word in ["doctor", "specialist", "ডাক্তার", "dekhabo", "hospital"]):
        return f"আপনার {condition}-এর জন্য একজন ডার্মাটোলজিস্ট দেখানো সবচেয়ে ভালো হবে।" if is_bengali else f"I recommend consulting a Dermatologist for your {condition}."
    elif any(word in q for word in ["medicine", "cream", "ঔষধ", "osud", "lagabo"]):
        return f"⚠️ সতর্ক: {condition}-এর ওপর ডাক্তারের পরামর্শ ছাড়া কিছু লাগাবেন না।" if is_bengali else f"⚠️ Warning: Do not apply medicine for {condition} without a prescription."
    elif any(word in q for word in ["care", "tips", "যত্ন", "what to do"]):
        return f"✅ পরামর্শ: আক্রান্ত জায়গাটি পরিষ্কার রাখুন এবং রোদ এড়িয়ে চলুন।" if is_bengali else f"✅ Advice: Keep the area clean and avoid direct sunlight."
    else:
        return f"আপনার {condition} সম্পর্কে আর কী জানতে চান?" if is_bengali else f"How else can I help you with {condition}?"

# ৪. গুগল ড্রাইভ থেকে মডেল লোড (উন্নত পদ্ধতি)
@st.cache_resource
def load_my_model():
    # সরাসরি ড্রাইভের ফাইল আইডি ব্যবহার করা হয়েছে
    file_id = '1Ey5AKBM5FA0wcj2_SMiJ01l0RWf2XIAL'
    drive_url = f'https://drive.google.com/uc?id={file_id}'
    model_path = 'skin_cancer_model.h5'
    
    if not os.path.exists(model_path):
        with st.spinner('মডেল ডাউনলোড হচ্ছে... এটি ২-৩ মিনিট সময় নিতে পারে।'):
            try:
                # gdown এর বিকল্প কমান্ড যা বড় ফাইলের জন্য ভালো কাজ করে
                output = gdown.download(drive_url, model_path, quiet=False, fuzzy=True)
                if output is None:
                    # যদি uc লিঙ্ক কাজ না করে তবে সরাসরি ডাউনলোড ট্রাই করবে
                    drive_url_alt = f'https://drive.google.com/open?id={file_id}&export=download'
                    gdown.download(drive_url_alt, model_path, quiet=False)
            except Exception:
                st.error("ডাউনলোড পুনরায় ব্যর্থ হয়েছে। ড্রাইভের পারমিশন 'Anyone with the link' আছে কি না চেক করুন।")
                return None
            
    return tf.keras.models.load_model(model_path, compile=False)

# ৫. মেইন ইন্টারফেস
st.title("🩺 SkinAI Professional Assistant")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📸 Upload Skin Image")
    file = st.file_uploader("", type=["jpg", "png", "jpeg"])
    if file:
        img = Image.open(file).convert('RGB')
        st.image(img, use_container_width=True)

with col2:
    if file and model:
        img_res = img.resize((100, 75))
        x = np.asarray(img_res) / 255.0
        x = np.expand_dims(x, axis=0)
        pred = model.predict(x, verbose=0)
        result = classes[np.argmax(pred)]
        
        st.success(f"### Detection Result: {result}")
        st.markdown("---")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        chat_container = st.container(height=350)
        with chat_container:
            for m in st.session_state.messages:
                with st.chat_message(m["role"], avatar="👨‍💻" if m["role"] == "user" else "🤖"):
                    st.markdown(m["content"])

        if prompt := st.chat_input("বাংলা বা English-এ প্রশ্ন করুন..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user", avatar="👨‍💻"): st.markdown(prompt)
                reply = get_natural_response(prompt, result)
                with st.chat_message("assistant", avatar="🤖"): st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.session_state.messages.append({"role": "assistant", "content": reply})
                with st.chat_message("assistant", avatar="🤖"):
                    reply = get_natural_response(prompt, result)
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
