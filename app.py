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
        "all_options": [
            "Road Accident", "Heavy Bleeding", "Chest Pain",
            "Breathing Problem", "Burn Injury", "Fever",
            "Headache", "Stomach Ache", "Dizziness"
        ],
        "selected_problems": [],
        "typed_text": "",
        "voice_text": ""
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ---------------- HELPERS ----------------
def split_problems(text):
    text = text.lower()
    for sep in [",", "&", " and "]:
        text = text.replace(sep, "|")
    return [p.strip().title() for p in text.split("|") if p.strip()]

def add_problems(problem_list):
    for p in problem_list:
        if p not in st.session_state.all_options:
            st.session_state.all_options.append(p)
        if p not in st.session_state.selected_problems:
            st.session_state.selected_problems.append(p)

# ---------------- HEADER ----------------
st.title("🚨 Golden Hour")
st.subheader("AI Emergency Decision Assistant")
st.divider()

# ---------------- LAYOUT ----------------
main, side = st.columns([3, 1])

# ================= MAIN =================
with main:

    # -------- SELECT --------
    st.write("### Select all that apply")
    st.multiselect(
        "",
        st.session_state.all_options,
        key="selected_problems"
    )

    # -------- TEXT INPUT --------
    st.write("### ➕ Add your problem (type multiple)")
    col1, col2 = st.columns([3, 1])

    with col1:
        st.text_input(
            "",
            placeholder="fever, headache and dizziness",
            key="typed_text"
        )

    with col2:
        if st.button("Add Text"):
            problems = split_problems(st.session_state.typed_text)
            add_problems(problems)
            st.session_state["typed_text"] = ""
            st.rerun()

    # -------- VOICE INPUT --------
    st.divider()
    st.write("### 🎙️ Describe the problem using voice")

    audio_bytes = audio_recorder("Click to record")

    if audio_bytes:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_bytes)
            audio_path = f.name

        r = sr.Recognizer()
        try:
            with sr.AudioFile(audio_path) as src:
                audio = r.record(src)
            st.session_state["voice_text"] = r.recognize_google(audio)
        except sr.UnknownValueError:
            st.error("Could not understand the voice")
        except Exception:
            st.error("Voice recognition failed")
        finally:
            os.remove(audio_path)

    # -------- VOICE TEXT BOX --------
    col3, col4 = st.columns([3, 1])

    with col3:
        st.text_input(
            "📝 Recognized Voice",
            key="voice_text",
            placeholder="Voice input appears here"
        )

    with col4:
        if st.button("Add Voice"):
            problems = split_problems(st.session_state.voice_text)
            add_problems(problems)
            st.session_state["voice_text"] = ""
            st.rerun()

# ================= SIDEBAR =================
with side:
    st.write("### 📋 All Added Problems")
    if st.session_state.selected_problems:
        for p in st.session_state.selected_problems:
            st.success(p)
    else:
        st.info("No problems added yet")

# ---------------- SEVERITY ----------------
if not st.session_state.selected_problems:
    st.warning("Please add at least one problem.")
    st.stop()

severity = "Urgent"
for p in st.session_state.selected_problems:
    if classify_severity(p) == "Severe":
        severity = "Severe"
        break

def maps_link(level):
    q = "trauma hospital near me" if level == "Severe" else "hospital near me"
    return f"https://www.google.com/maps/search/{q.replace(' ', '+')}"

st.divider()

# ---------------- RESULT ----------------
if severity == "Severe":
    st.error("🔴 SEVERE EMERGENCY")
    st.write("📞 Call emergency services immediately")
    st.write("🩸 Provide basic first aid")
    st.markdown(f"[🧭 Find Trauma Hospitals]({maps_link(severity)})")

else:
    st.warning("🟠 URGENT MEDICAL ATTENTION NEEDED")
    st.markdown(f"[🧭 Find Nearby Hospitals]({maps_link(severity)})")
