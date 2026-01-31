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
        "Chest Pain",
        "Breathing Problem",
        "Heavy Bleeding",
        "Road Accident",
        "Burn Injury"
    ]
    matched = [s for s in symptoms if s in severe_indicators]

    if severity == "Severe" and matched:
        return (
            "⚠️ **Why this is severe?**\n\n"
            f"The selected symptom(s) **{', '.join(matched)}** are commonly associated "
            "with life-threatening conditions that require immediate medical attention."
        )

    return (
        "ℹ️ **Why this is urgent?**\n\n"
        "The selected symptoms do not immediately indicate life-threatening trauma, "
        "but they still require prompt medical evaluation."
    )

# ---------------- AI CHAT FUNCTION ----------------
def ai_free_chat(user_question, symptoms, severity, role):
    q = user_question.lower()
    symptom_text = ", ".join(symptoms) if symptoms else "the reported symptoms"

    if any(word in q for word in ["severe", "serious", "danger", "life"]):
        return (
            f"Based on **{symptom_text}**, this case is classified as **{severity}**. "
            "Severe cases may involve life-threatening conditions and should not be delayed."
        )

    if any(word in q for word in ["what should", "what to do", "next step", "now"]):
        if severity == "Severe":
            return (
                "You should seek **immediate emergency medical care**. "
                "Call emergency services and go to the nearest trauma hospital."
            )
        return (
            "It is advisable to consult a medical professional soon and monitor symptoms closely."
        )

    if any(word in q for word in ["cpr", "first aid"]):
        return (
            "CPR may be required if the patient is unresponsive and not breathing normally. "
            "Only perform CPR if you are trained. Please refer to the CPR video provided above."
        )

    if any(word in q for word in ["hospital", "doctor", "clinic"]):
        return (
            "Visiting a nearby hospital is recommended based on the current symptoms. "
            "Use the hospital locator provided to find the nearest facility."
        )

    if role == "👥 I am helping someone else":
        return (
            "As a helper, ensure your own safety first, avoid unnecessary movement of the patient, "
            "and follow emergency service instructions carefully."
        )

    return (
        "I understand your concern. Based on the available information, "
        "please continue monitoring the symptoms and seek medical help if the condition worsens."
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
    st.info("⚠️ Your safety comes first. Stay calm and act quickly.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🧍‍♂️ Scene Safety")
        st.markdown("✅ Ensure the area is safe")
        st.markdown("🚫 Do NOT move the patient unnecessarily")

    with col2:
        st.markdown("### 🩺 Patient Check")
        st.markdown("🫁 Check breathing & responsiveness")
        st.markdown("🩸 Apply pressure if bleeding")
        st.markdown("❤️ **Learn CPR:** [Watch CPR Video](https://youtu.be/2PngCv7NjaI)")

    st.divider()

# ---------------- SYMPTOMS ----------------
if st.session_state.user_role:

    main, side = st.columns([3, 1])

    with main:
        st.multiselect(
            "Select symptoms",
            st.session_state.options,
            key="ui_selected"
        )
        add_symptoms(st.session_state.ui_selected)

    with side:
        st.write("### 📋 Reported Symptoms")
        for s in st.session_state.all_symptoms:
            st.success(s)

    if not st.session_state.all_symptoms:
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

    st.info(explain_severity(st.session_state.all_symptoms, severity))

    # ---------------- AI CHATBOX ----------------
    st.divider()
    st.markdown("### 💬 Ask the AI Emergency Assistant")

    user_question = st.chat_input("Ask anything about the emergency...")

    if user_question:
        with st.chat_message("user"):
            st.write(user_question)

        with st.chat_message("assistant"):
            st.write(
                ai_free_chat(
                    user_question,
                    st.session_state.all_symptoms,
                    severity,
                    st.session_state.user_role
                )
            )

# ---------------- RESET ----------------
st.divider()
if st.button("🔄 Start New Emergency"):
    st.session_state.clear()
    init_state()
    st.rerun()
