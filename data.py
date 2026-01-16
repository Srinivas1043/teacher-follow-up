import streamlit as st
from auth import supabase

def get_students(user_id):
    """Fetch all students for a specific teacher."""
    try:
        response = supabase.table("students").select("*").eq("user_id", user_id).order("name").execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching students: {e}")
        return []

def add_student(user_id, name, grade, notes=""):
    """Add a new student."""
    try:
        data = {
            "user_id": user_id,
            "name": name,
            "grade": grade,
            "notes": notes
        }
        response = supabase.table("students").insert(data).execute()
        return response.data
    except Exception as e:
        st.error(f"Error adding student: {e}")
        return None

def save_followup(student_id, content, original_remarks):
    """Save a generated follow-up."""
    try:
        data = {
            "student_id": student_id,
            "content": content,
            "original_remarks": original_remarks
        }
        response = supabase.table("followups").insert(data).execute()
        return response.data
    except Exception as e:
        st.error(f"Error saving follow-up: {e}")
        return None

def get_student_followups(student_id):
    """Fetch history for a student."""
    try:
        response = supabase.table("followups").select("*").eq("student_id", student_id).order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching history: {e}")
        return []
