# 🚨 Golden Hour – AI Emergency Decision Assistant

## Problem Statement
In emergency situations, panic and delayed decision-making can cost lives.
The first 60 minutes after a traumatic injury — known as the *Golden Hour* —
are critical for survival.

Golden Hour is a decision-support system that provides instant guidance
during trauma emergencies to help users take the right actions quickly
before reaching professional medical care.

---

## Scope of the Project
This system focuses only on **trauma-related emergencies**, such as:
- Road accidents
- Heavy bleeding
- Burn injuries
- Unconscious patients

The system does **not** perform medical diagnosis and does not replace doctors.

---

## System Architecture (Simple)

User Interface (Streamlit)
↓
Emergency Input Processing
↓
Severity Classification Engine
↓
Action Guidance + Hospital Navigation


The architecture separates UI, decision logic, and navigation for clarity
and future scalability.

---

## Tech Stack
- **Frontend & Backend:** Python
- **UI Framework:** Streamlit
- **Mapping:** Google Maps (via search links)

---

## AI Tools Used
- Rule-based AI logic for emergency severity classification
- Decision-support logic inspired by emergency triage principles

No external AI APIs are used in this version to ensure stability
and reproducibility during evaluation.

---

## Prompt Strategy Summary
Although no LLM API is used directly, the system follows a structured
prompt-like decision strategy:
- Convert user-selected symptoms into standardized categories
- Classify severity as *Severe* or *Urgent*
- Provide safe, non-diagnostic, and actionable guidance
- Reduce cognitive load during panic situations

(Planned future enhancement: LLM-based free-text understanding)

---

## Features
- Multiple emergency selection
- Custom emergency input
- Emergency severity classification
- Panic Mode for high-stress situations
- Google Maps navigation to appropriate hospitals
- Clear medical disclaimer

---

## Setup Instructions
Follow these steps to run the project locally:

```bash
pip install -r requirements.txt
streamlit run app.py
