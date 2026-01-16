import os
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st

# Load secrets from the streamlit secrets file for this standalone check
try:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    print(f"✅ Credentials found in secrets.toml")
except Exception as e:
    print(f"❌ Could not load secrets: {e}")
    exit(1)

try:
    supabase: Client = create_client(url, key)
    print("✅ Supabase client initialized.")
except Exception as e:
    print(f"❌ Failed to initialize Supabase client: {e}")
    exit(1)

print("\n--- Checking Tables ---")

try:
    # Try to select from 'students' - limit 1 just to see if table exists
    response = supabase.table("students").select("*").limit(1).execute()
    print("✅ Table 'students' EXISTS and is accessible.")
    
    # Try 'followups'
    response = supabase.table("followups").select("*").limit(1).execute()
    print("✅ Table 'followups' EXISTS and is accessible.")

except Exception as e:
    print(f"❌ Table Check Failed: {e}")
    print("\n⚠️  LIKELY CAUSE: You have not run the SQL script in Supabase yet.")
    print("   Please copy the contents of 'supabase_setup.sql' and run it in the SQL Editor on your Supabase Dashboard.")
