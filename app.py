import streamlit as st
from emergency_data import classify_severity
from hospitals import get_maps_link

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Golden Hour", layout="centered")

# ---------------- HEADER ----------------
st.title("🚨 Golden Hour")
st.subheader("AI Emergency Decision Assistant")
st.write("Get instant guidance during medical emergencies.")

st.divider()

# ---------------- SESSION STATE ----------------
if "all_options" not in st.session_state:
    st.session_state.all_options = [
        "Road Accident",
        "Heavy Bleeding",
        "Burn Injury",
        "Unconscious Person"
    ]

if "selected_problems" not in st.session_state:
    st.session_state.selected_problems = []

if "custom_input" not in st.session_state:
    st.session_state.custom_input = ""

# ---------------- ADD CUSTOM PROBLEM ----------------
def add_problem():
    value = st.session_state.custom_input.strip()
    if value:
        if value not in st.session_state.all_options:
            st.session_state.all_options.append(value)
        if value not in st.session_state.selected_problems:
            st.session_state.selected_problems.append(value)
        st.session_state.custom_input = ""

# ---------------- MULTISELECT ----------------
st.write("## What is the emergency? (Select all that apply)")

st.session_state.selected_problems = st.multiselect(
    "",
    options=st.session_state.all_options,
    default=st.session_state.selected_problems
)

st.text_input(
    "➕ Add your problem (type & press Enter)",
    key="custom_input",
    on_change=add_problem
)

# ---------------- STOP IF EMPTY ----------------
if not st.session_state.selected_problems:
    st.info("Please select or type at least one problem.")
    st.stop()

st.divider()

# ---------------- SEVERITY DECISION ----------------
severity = "Urgent"
for problem in st.session_state.selected_problems:
    if classify_severity(problem) == "Severe":
        severity = "Severe"
        break

maps_link = get_maps_link(severity)

# ---------------- SEVERE ----------------
if severity == "Severe":
    st.error("🔴 SEVERE EMERGENCY")

    st.write("### Immediate Actions")
    st.write("📞 Call emergency services (108)")
    st.write("🩸 Apply pressure / basic first aid")
    st.write("🚑 Go to nearest trauma hospital")

    st.markdown(f"[🧭 View Nearby Trauma Hospitals]({maps_link})")

    st.divider()
    if st.button("🚨 PANIC MODE"):
        st.error("🚨 EMERGENCY MODE ACTIVATED")
        st.markdown("## 📞 CALL AMBULANCE NOW (108)")
        st.markdown("## 🩸 APPLY PRESSURE / FIRST AID")
        st.markdown("## 🚑 DO NOT DELAY HOSPITAL VISIT")

# ---------------- URGENT ----------------
else:
    st.warning("🟠 URGENT — MEDICAL ATTENTION NEEDED")

    st.write("### Recommended Actions")
    st.write("🏥 Visit nearby hospital or clinic")
    st.write("👩‍⚕️ Consult a medical professional")
    st.write("📅 Monitor symptoms carefully")

    st.markdown(f"[🧭 View Nearby Hospitals / Clinics]({maps_link})")
