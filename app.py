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

def explain_severity(symptoms, severity):
    severe_indicators = [
        "Chest Pain", "Breathing Problem",
        "Heavy Bleeding", "Road Accident", "Burn Injury"
    ]
    matched = [s for s in symptoms if s in severe_indicators]

    if severity == "Severe" and matched:
        return (
            "⚠️ **Why this is severe?**\n\n"
            f"The selected symptom(s) **{', '.join(matched)}** are commonly associated "
            "with potentially life-threatening conditions that require immediate care."
        )

    return (
        "ℹ️ **Why this is urgent?**\n\n"
        "The selected symptoms may worsen if ignored and should be evaluated by a medical professional."
    )

# ---------------- AI CHAT FUNCTION ----------------
def ai_free_chat(question, symptoms, severity, role):
    q = question.lower()
    symptom_text = ", ".join(symptoms) if symptoms else "the reported symptoms"

    if any(x in q for x in ["severe", "serious", "danger"]):
        return f"Based on **{symptom_text}**, this case is classified as **{severity}**, indicating potential medical risk."

    if any(x in q for x in ["what should", "what to do", "next"]):
        if severity == "Severe":
            return "You should immediately call emergency services and go to the nearest trauma hospital."
        return "You should consult a doctor soon and monitor symptoms carefully."

    if "cpr" in q or "first aid" in q:
        return "CPR should only be performed if the patient is unresponsive and not breathing normally. Use the CPR video provided above."

    if "hospital" in q or "doctor" in q:
        return "A hospital visit is advised. Use the hospital locator link above to find nearby facilities."

    if role == "👥 I am helping someone else":
        return "As a helper, ensure your own safety, avoid moving the patient unnecessarily, and follow emergency instructions."

    return (
        "I understand your concern. Based on the current information, "
        "please monitor the situation closely and seek medical help if symptoms worsen."
    )

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
    st.info("⚠️ Your safety comes first.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🧍‍♂️ Scene Safety")
        st.markdown("✅ Ensure the area is safe")
        st.markdown("🚫 Do NOT move the patient unnecessarily")

    with col2:
        st.markdown("### 🩺 Patient Check")
        st.markdown("🫁 Check breathing & responsiveness")
        st.markdown("🩸 Apply firm pressure if bleeding")
        st.markdown("❤️ **Learn CPR:** [Watch CPR Video](https://youtu.be/2PngCv7NjaI)")

    st.markdown(
        """
        🚑 **Emergency Action**
        - 📞 Call emergency services immediately
        - ⏱️ Every second matters during the *Golden Hour*
        """
    )

    st.markdown(
        """
        <a href="tel:108">
            <button style="background:#e53935;color:white;padding:14px 26px;
            border:none;border-radius:10px;font-size:18px;">
                📞 Call 108 Now
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )
    st.divider()

# ---------------- SYMPTOMS ----------------
if st.session_state.user_role:
    main, side = st.columns([3, 1])

    with main:
        st.write("### Select symptoms")
        selected = st.multiselect("", st.session_state.options, key="ui_selected")
        add_symptoms(selected)

        st.divider()
        st.write("### ➕ How do you want to add symptoms?")
        st.radio("", ["✍️ Add via Text", "🎙️ Add via Voice"], key="input_mode", horizontal=True)

        if st.session_state.input_mode == "✍️ Add via Text":
            with st.form("text_form", clear_on_submit=True):
                txt = st.text_input("Enter symptoms", placeholder="fever, headache")
                if st.form_submit_button("Add") and txt:
                    add_symptoms(split_text(txt))

        if st.session_state.input_mode == "🎙️ Add via Voice":
            audio = audio_recorder("")
            if audio:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                    f.write(audio)
                    path = f.name
                r = sr.Recognizer()
                try:
                    with sr.AudioFile(path) as src:
                        audio_data = r.record(src)
                    st.session_state.voice_text = r.recognize_google(audio_data)
                except:
                    st.error("Voice recognition failed")
                finally:
                    os.remove(path)

            with st.form("voice_form", clear_on_submit=True):
                voice = st.text_input("Recognized voice", value=st.session_state.voice_text)
                if st.form_submit_button("Add Voice") and voice:
                    add_symptoms(split_text(voice))

    with side:
        st.write("### 📋 Reported Symptoms")
        for s in st.session_state.all_symptoms:
            st.success(s)

    if not st.session_state.all_symptoms:
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

    st.info(explain_severity(st.session_state.all_symptoms, severity))

    # ---------------- AI CHAT BOX ----------------
    st.divider()
    st.markdown("### 💬 AI Emergency Assistant")

    question = st.chat_input("Ask anything about the emergency…")
    if question:
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            st.write(ai_free_chat(
                question,
                st.session_state.all_symptoms,
                severity,
                st.session_state.user_role
            ))

# ---------------- PATIENT CALL ----------------
if st.session_state.user_role == "👤 I am the patient":
    st.divider()
    st.error("📞 If you are in immediate danger, contact emergency services now.")
    st.markdown(
        """
        <a href="tel:108">
            <button style="background:#ff4b4b;color:white;padding:16px 32px;
            border:none;border-radius:12px;font-size:20px;">
                📞 Call 108 (Emergency)
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )

# ---------------- FOOTER IMAGE ----------------
st.divider()
IMAGE_PATH = "assets/goldenhour.jpg"
if os.path.exists(IMAGE_PATH):
    st.image(IMAGE_PATH, caption="⏱️ The Golden Hour – Immediate action saves lives", use_column_width=True)

# ---------------- RESET ----------------
st.divider()
if st.button("🔄 Start New Emergency"):
    st.session_state.clear()
    init_state()
    st.rerun()
