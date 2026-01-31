import streamlit as st
import speech_recognition as sr
import tempfile
import os
import time
from audio_recorder_streamlit import audio_recorder
from emergency_data import classify_severity

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Golden Hour", layout="wide")

# ---------------- SESSION STATE INIT ----------------
def init_state():
    defaults = {
        "user_role": None,
        "options": [
            "Road Accident", "Heavy Bleeding", "Chest Pain",
            "Breathing Problem", "Burn Injury", "Fever",
            "Headache", "Stomach Ache", "Dizziness"
        ],
        "ui_selected": [],
        "all_symptoms": [],
        "voice_text": "",
        "input_mode": "✍️ Add via Text",
        "last_activity": time.time()
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ---------------- HELPERS ----------------
def update_activity():
    st.session_state.last_activity = time.time()

def split_text(text):
    for sep in [",", "&", " and "]:
        text = text.replace(sep, "|")
    return [t.strip().title() for t in text.split("|") if t.strip()]

def add_symptoms(items):
    for s in items:
        if s not in st.session_state.options:
            st.session_state.options.append(s)
        if s not in st.session_state.all_symptoms:
            st.session_state.all_symptoms.append(s)
    update_activity()

def maps_link(level="normal"):
    query = "trauma hospital near me" if level == "severe" else "hospital near me"
    return f"https://www.google.com/maps/search/{query.replace(' ', '+')}"

# ---------------- HEADER ----------------
st.title("🚨 Golden Hour")
st.subheader("AI Emergency Decision Assistant")
st.divider()

# ---------------- ROLE SELECTION ----------------
st.write("## Who is using this website?")
st.radio(
    "",
    ["👤 I am the patient", "👥 I am helping someone else"],
    key="user_role",
    on_change=update_activity
)

# ---------------- HELPER GUIDELINES ----------------
if st.session_state.user_role == "👥 I am helping someone else":
    st.markdown("## 🛟 Helper Safety & First-Aid Guidelines")

    st.info("⚠️ Your safety comes first. Stay calm and act quickly.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🧍‍♂️ Scene Safety")
        st.markdown("✅ Ensure the area is safe before approaching")
        st.markdown("🚫 Do NOT move the patient unless there is danger")

    with col2:
        st.markdown("### 🩺 Patient Check")
        st.markdown("🫁 Check breathing & responsiveness")
        st.markdown("🩸 Apply firm pressure if there is bleeding")

    st.markdown("---")

    st.markdown(
        """
        🚑 **Emergency Action**
        - 📞 Call emergency services immediately
        - 🗣️ Speak clearly and follow instructions
        - ⏱️ Every second matters during the *Golden Hour*
        """
    )

    # 🔴 CALL 108 (HELPER)
    st.markdown(
        """
        <a href="tel:108" style="text-decoration:none;">
            <button style="
                background-color:#e53935;
                color:white;
                padding:14px 26px;
                font-size:18px;
                border:none;
                border-radius:10px;
                cursor:pointer;
                margin-top:10px;
            ">
                📞 Call 108 Now
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )

    st.success("⬇️ Now, please report the patient’s symptoms")
    st.divider()

# ---------------- SYMPTOMS SECTION ----------------
if st.session_state.user_role:

    main, side = st.columns([3, 1])

    with main:
        st.write("### Select symptoms")
        selected = st.multiselect(
            "",
            st.session_state.options,
            key="ui_selected",
            on_change=update_activity
        )
        if selected:
            add_symptoms(selected)

        st.divider()
        st.write("### ➕ How do you want to add symptoms?")

        st.radio(
            "",
            ["✍️ Add via Text", "🎙️ Add via Voice"],
            key="input_mode",
            horizontal=True
        )

        # -------- ADD VIA TEXT --------
        if st.session_state.input_mode == "✍️ Add via Text":
            with st.form("text_form", clear_on_submit=True):
                text_input = st.text_input(
                    "Enter symptoms",
                    placeholder="fever, headache and dizziness"
                )
                if st.form_submit_button("Add Text") and text_input.strip():
                    add_symptoms(split_text(text_input))

        # -------- ADD VIA VOICE --------
        if st.session_state.input_mode == "🎙️ Add via Voice":
            st.write("🎤 Click to record")
            audio_bytes = audio_recorder("")

            if audio_bytes:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                    f.write(audio_bytes)
                    path = f.name

                r = sr.Recognizer()
                try:
                    with sr.AudioFile(path) as src:
                        audio = r.record(src)
                    st.session_state.voice_text = r.recognize_google(audio)
                except:
                    st.error("Voice recognition failed")
                finally:
                    os.remove(path)

            with st.form("voice_form", clear_on_submit=True):
                voice_input = st.text_input(
                    "📝 Recognized voice",
                    value=st.session_state.voice_text
                )
                if st.form_submit_button("Add Voice") and voice_input.strip():
                    add_symptoms(split_text(voice_input))

    with side:
        st.write("### 📋 Reported Symptoms")
        if st.session_state.all_symptoms:
            for s in st.session_state.all_symptoms:
                st.success(s)
        else:
            st.info("No symptoms added yet")

    if not st.session_state.all_symptoms:
        st.warning("Please add at least one symptom.")
        st.stop()

    # ---------------- SEVERITY ----------------
    severity = "Urgent"
    for s in st.session_state.all_symptoms:
        if classify_severity(s) == "Severe":
            severity = "Severe"
            break

    st.divider()

    if severity == "Severe":
        st.error("🔴 SEVERE EMERGENCY")
        st.markdown(f"[🧭 Find Trauma Hospitals]({maps_link('severe')})")
    else:
        st.warning("🟠 MEDICAL ATTENTION ADVISED")
        st.markdown(f"[🧭 Find Nearby Hospitals]({maps_link()})")

# ---------------- PATIENT EMERGENCY CALL ----------------
if st.session_state.user_role == "👤 I am the patient":
    st.divider()
    st.markdown("## 🚨 Emergency Contact")

    st.error("📞 If you are in immediate danger, contact emergency services now.")

    st.markdown(
        """
        <a href="tel:108" style="text-decoration:none;">
            <button style="
                background-color:#ff4b4b;
                color:white;
                padding:16px 32px;
                font-size:20px;
                border:none;
                border-radius:12px;
                cursor:pointer;
            ">
                📞 Call 108 (Emergency)
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )

# ---------------- FOOTER IMAGE ----------------
st.divider()
IMAGE_PATH = "golden_hour...jpg"   # make sure this file exists in same folder as app.py

if os.path.exists(IMAGE_PATH):
    st.image(
        IMAGE_PATH,
        caption="⏱️ The Golden Hour – Immediate action saves lives",
        width=900
    )

# ---------------- RESET ----------------
st.divider()
if st.button("🔄 Start New Emergency"):
    st.session_state.clear()
    init_state()
    st.rerun()
