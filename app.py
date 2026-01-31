import streamlit as st
import speech_recognition as sr
import tempfile
import os
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
        "reset_trigger": False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ---------------- SAFE RESET HANDLER ----------------
if st.session_state.reset_trigger:
    st.session_state.all_symptoms = []
    st.session_state.ui_selected = []
    st.session_state.voice_text = ""
    st.session_state.pop("user_role", None)  # SAFE reset for radio
    st.session_state.reset_trigger = False
    st.rerun()

# ---------------- HELPER FUNCTIONS ----------------
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

def maps_link(level="normal"):
    query = "trauma hospital near me" if level == "severe" else "hospital near me"
    return f"https://www.google.com/maps/search/{query.replace(' ', '+')}"

# ---------------- HEADER ----------------
st.title("🚨 Golden Hour")
st.subheader("AI Emergency Decision Assistant")

# ---------------- IMAGE (SAME LOGIC) ----------------
IMAGE_PATH = "goldenhour.png"
if os.path.exists(IMAGE_PATH):
    st.image(IMAGE_PATH, use_column_width=True)

st.divider()

# ---------------- ROLE SELECTION ----------------
st.write("## Who is using this website?")
st.radio(
    "",
    ["👤 I am the patient", "👥 I am helping someone else"],
    key="user_role"
)

# ---------------- HELPER GUIDELINES ----------------
if st.session_state.user_role == "👥 I am helping someone else":
    st.info("👥 **Helper Safety & First-Aid Guidelines**")
    st.write("• Ensure the area is safe")
    st.write("• Do NOT move the patient unnecessarily")
    st.write("• Apply pressure if bleeding")
    st.write("• Check breathing and responsiveness")
    st.write("• Call emergency services immediately")
    st.divider()
    st.success("⬇️ Now report the patient’s symptoms")

# ================= SYMPTOMS (PATIENT + HELPER) =================
if st.session_state.user_role:

    main, side = st.columns([3, 1])

    # -------- MAIN --------
    with main:
        st.write("### Select symptoms")
        selected = st.multiselect(
            "",
            st.session_state.options,
            key="ui_selected"
        )
        if selected:
            add_symptoms(selected)

        st.write("### ➕ Add via text")
        with st.form("text_form", clear_on_submit=True):
            text_input = st.text_input("", placeholder="fever, headache and dizziness")
            if st.form_submit_button("Add Text") and text_input.strip():
                add_symptoms(split_text(text_input))

        st.divider()
        st.write("### 🎙️ Add via voice")
        audio_bytes = audio_recorder("Click to record")

        if audio_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(audio_bytes)
                audio_path = f.name

            recognizer = sr.Recognizer()
            try:
                with sr.AudioFile(audio_path) as source:
                    audio = recognizer.record(source)
                st.session_state.voice_text = recognizer.recognize_google(audio)
            except:
                st.error("Voice recognition failed")
            finally:
                os.remove(audio_path)

        with st.form("voice_form", clear_on_submit=True):
            voice_input = st.text_input("📝 Recognized voice", value=st.session_state.voice_text)
            if st.form_submit_button("Add Voice") and voice_input.strip():
                add_symptoms(split_text(voice_input))

    # -------- SIDEBAR --------
    with side:
        st.write("### 📋 Reported Symptoms")
        if st.session_state.all_symptoms:
            for s in st.session_state.all_symptoms:
                st.success(s)
        else:
            st.info("No symptoms added yet")

    # -------- SEVERITY --------
    if not st.session_state.all_symptoms:
        st.warning("Please add at least one symptom.")
        st.stop()

    severity = "Urgent"
    for s in st.session_state.all_symptoms:
        if classify_severity(s) == "Severe":
            severity = "Severe"
            break

    st.divider()

    if severity == "Severe":
        st.error("🔴 SEVERE EMERGENCY")
        st.write("📞 Call emergency services immediately")
        st.markdown(f"[🧭 Find Trauma Hospitals]({maps_link('severe')})")
    else:
        st.warning("🟠 MEDICAL ATTENTION ADVISED")
        st.markdown(f"[🧭 Find Nearby Hospitals]({maps_link()})")
        # ---------------- SAFE IMAGE LOAD ---------------- IMAGE_PATH = "assets/goldenhour.png" if os.path.exists(IMAGE_PATH): st.image(IMAGE_PATH, use_column_width=True) else: st.warning("⚠️ Banner image not found. (assets/goldenhour.png)")

    # ---------------- START NEW EMERGENCY (LAST ONLY) ----------------
    st.divider()
    if st.button("🔄 Start New Emergency"):
        st.session_state.reset_trigger = True
        st.rerun()
