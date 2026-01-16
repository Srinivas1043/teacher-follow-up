import google.generativeai as genai
import streamlit as st
import os

# Load secrets directly or via streamlit
try:
    api_key = st.secrets["gemini"].get("api_key")
    if not api_key:
        print("❌ API Key not found in secrets.")
        exit(1)
    
    genai.configure(api_key=api_key)
    
    print("--- Available Models ---")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            
except Exception as e:
    print(f"❌ Error: {e}")
