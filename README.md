# 🚨 Golden Hour – AI Emergency Decision Assistant

## Problem Statement
During trauma emergencies, panic and delayed decisions can cost lives.
Golden Hour provides instant AI-guided actions during the critical first 60 minutes
after an accident or injury.

## Scope
This system focuses only on **trauma emergencies**:
- Road accidents
- Heavy bleeding
- Burn injuries
- Unconscious patients

## Features
- Emergency severity classification
- Immediate action guidance
- Panic Mode for high-stress situations
- Trauma hospital recommendation

## System Architecture
Frontend (Streamlit)  
→ Emergency Severity Engine  
→ Action Guidance Module  
→ Hospital Recommendation

## Tech Stack
- Python
- Streamlit

## AI Usage
AI logic is used for emergency severity classification and decision support.
This system does **not** perform diagnosis.

## Prompt Strategy
Structured prompts are used to ensure deterministic and safe outputs.

## Setup Instructions
```bash
pip install -r requirements.txt
streamlit run app.py
