import streamlit as st
import speech_recognition as sr
import tempfile, os
from audio_recorder_streamlit import audio_recorder
from emergency_data import classify_severity

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Golden Hour", layout="wide")

# ---------------- INIT SESSION STATE ----------------
def init_state():
    defaults = {
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

# ---------------- HANDLE RESET EARLY ----------------
if st.session_state.reset_trigger:
    st.session_state.all_symptoms = []
    st.session_state.ui_selected = []
    st.session_state.voice_text = ""
    st.session_state.reset_trigger = False
    st.rerun()

# ---------------- HELPERS ----------------
def split_text(text):
    text = text.lower()
    for sep in [",", "&", " and "]:
        text = text.replace(sep, "|")
    return [t.strip().title() for t in text.split("|") if t.strip()]

def add_symptoms(items):
    for s in items:
        if s not in st.session_state.options:
            st.session_state.options.append(s)
        if s not in st.session_state.all_symptoms:
            st.session_state.all_symptoms.append(s)

# ---------------- HEADER ----------------
st.title("🚨 Golden Hour")
st.subheader("AI Emergency Decision Assistant")
st.divider()

main, side = st.columns([3, 1])

# ================= MAIN =================
with main:

    # -------- MULTISELECT --------
    st.write("### Select all that apply")
    selected = st.multiselect(
        "",
        st.session_state.options,
        key="ui_selected"
    )

    if selected:
        add_symptoms(selected)

    # -------- TEXT INPUT --------
    st.write("### ➕ Add via text")
    with st.form("text_form", clear_on_submit=True):
        text_input = st.text_input(
            "",
            placeholder="fever, headache and dizziness"
        )
        if st.form_submit_button("Add Text") and text_input.strip():
            add_symptoms(split_text(text_input))

    # -------- VOICE INPUT --------
    st.divider()
    st.write("### 🎙️ Add via voice")

    audio_bytes = audio_recorder("Click to record")

    if audio_bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_bytes)
            audio_path = f.name

        r = sr.Recognizer()
        try:
            with sr.AudioFile(audio_path) as source:
                audio = r.record(source)
            st.session_state.voice_text = r.recognize_google(audio)
        except sr.UnknownValueError:
            st.error("Could not understand the voice")
        except Exception:
            st.error("Voice recognition failed")
        finally:
            os.remove(audio_path)

    with st.form("voice_form", clear_on_submit=True):
        voice_input = st.text_input(
            "📝 Recognized voice",
            value=st.session_state.voice_text
        )
        if st.form_submit_button("Add Voice") and voice_input.strip():
            add_symptoms(split_text(voice_input))

# ================= SIDEBAR =================
with side:
    st.write("### 📋 All Added Symptoms")

    if st.session_state.all_symptoms:
        for s in st.session_state.all_symptoms:
            st.success(s)
    else:
        st.info("No symptoms added yet")

    st.divider()

    if st.button("🗑️ Reset All Symptoms"):
        st.session_state.reset_trigger = True
        st.rerun()

# ---------------- SEVERITY ----------------
if not st.session_state.all_symptoms:
    st.warning("Please add at least one symptom.")
    st.stop()

severity = "Urgent"
for s in st.session_state.all_symptoms:
    if classify_severity(s) == "Severe":
        severity = "Severe"
        break

def maps_link(level):
    q = "trauma hospital near me" if level == "Severe" else "hospital near me"
    return f"https://www.google.com/maps/search/{q.replace(' ', '+')}"

st.divider()

if severity == "Severe":
    st.error("🔴 SEVERE EMERGENCY")
    st.markdown(f"[🧭 Find Trauma Hospitals]({maps_link(severity)})")
else:
    st.warning("🟠 URGENT MEDICAL ATTENTION NEEDED")
    st.markdown(f"[🧭 Find Nearby Hospitals]({maps_link(severity)})")
