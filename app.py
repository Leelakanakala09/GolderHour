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
        "last_activity": time.time(),
        "confirm_reset": False,
        "input_mode": "✍️ Add via Text"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ---------------- AUTO RESET AFTER 5 MIN ----------------
AUTO_RESET_TIME = 300

if time.time() - st.session_state.last_activity > AUTO_RESET_TIME:
    st.session_state.clear()
    init_state()
    st.rerun()

def update_activity():
    st.session_state.last_activity = time.time()

# ---------------- HELPERS ----------------
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
    st.info("👥 **Helper Safety & First-Aid Guidelines**")
    st.write("• Ensure the area is safe")
    st.write("• Do NOT move the patient unnecessarily")
    st.write("• Apply pressure if bleeding")
    st.write("• Check breathing and responsiveness")
    st.write("• Call emergency services immediately")
    st.divider()

# ================= SYMPTOMS =================
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
            horizontal=True,
            on_change=update_activity
        )

        if st.session_state.input_mode == "✍️ Add via Text":
            with st.form("text_form", clear_on_submit=True):
                text_input = st.text_input(
                    "Enter symptoms",
                    placeholder="fever, headache and dizziness"
                )
                if st.form_submit_button("Add Text") and text_input.strip():
                    add_symptoms(split_text(text_input))

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
                    update_activity()
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

    st.divider()
    st.write("### 🔄 Start New Emergency")

    if st.button("Start New Emergency"):
        st.session_state.clear()
        init_state()
        st.rerun()
# ---------------- FOOTER IMAGE ----------------
st.divider()

try:
    st.image(
        "goldenhour.png",
        caption="⏱️ The Golden Hour – Immediate action saves lives",
        width=900
    )
except Exception as e:
    st.warning("⚠️ Image could not be loaded")
    st.text(str(e))
# ---------------- FOOTER IMAGE (GOLDEN HOUR) ----------------
st.divider()
st.image(
    "https://raw.githubusercontent.com/Leelakanakala09/GoldenHour/main/goldenhour.png",
    caption="⏱️ The Golden Hour – Immediate action saves lives",
    use_column_width=True
)

)
