import streamlit as st
import auth
import time

# Page configuration
st.set_page_config(
    page_title="Teacher Follow-up Assistant",
    page_icon="🍎",
    layout="wide"
)

# Initialize Session State
if "user" not in st.session_state:
    st.session_state.user = None

def main():
    if st.session_state.user:
        # User is logged in, show the main dashboard
        show_dashboard()
    else:
        # User is not logged in, show login page
        show_login_page()

def show_login_page():
    st.title("🍎 Teacher Follow-up Assistant")
    st.markdown("### Welcome! Please log in to manage your students.")

    st.markdown("##### Sign In / Sign Up")
    st.info("Enter your email and password. If you are new, we will create an account for you automatically!")

    with st.form("auth_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Start using App 🚀")
    
    if submit:
        if email and password:
            with st.spinner("Authenticating..."):
                success, result = auth.sign_in_or_sign_up(email, password)
                
                if success:
                    st.session_state.user = result
                    st.success("Welcome!")
                    time.sleep(1)
                    st.rerun()
                else:
                    if "check your email" in str(result).lower():
                        st.warning(result)
                        st.markdown("""
                        **Stuck?** Go to your [Supabase Dashboard > Auth > Providers > Email](https://supabase.com/dashboard) 
                        and **Disable 'Confirm Email'** to skip this step in the future.
                        """)
                    else:
                        st.error(result)
        else:
            st.warning("Please enter both email and password.")

def show_dashboard():
    user = st.session_state.user
    
    # Sidebar
    st.sidebar.title(f"🍎 Teacher's Desk")
    st.sidebar.write(f"Logged in as: {user.email}")
    
    page = st.sidebar.radio("Navigate", ["Generate Follow-up", "My Students", "Student Analytics"])
    
    if st.sidebar.button("Log Out"):
        auth.supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()

    # --- PAGE: MY STUDENTS ---
    if page == "My Students":
        st.title("👨‍🎓 My Students")
        
        # Add Student Section
        with st.expander("➕ Add New Student"):
            with st.form("add_student_form"):
                col1, col2 = st.columns(2)
                name = col1.text_input("Student Name")
                grade = col2.text_input("Grade/Class")
                notes = st.text_area("Initial Notes (Optional)")
                submitted = st.form_submit_button("Add Student")
                
                if submitted:
                    if name:
                        import data
                        res = data.add_student(user.id, name, grade, notes)
                        if res:
                            st.success(f"Added {name} successfully!")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.warning("Name is required.")

        # List Students
        import data
        students = data.get_students(user.id)
        
        if students:
            st.markdown("### Class Roster")
            for student in students:
                with st.expander(f"{student['name']} ({student['grade']})"):
                    st.write(f"**Notes:** {student.get('notes', '')}")
                    st.caption(f"Added: {student['created_at'].split('T')[0]}")
        else:
            st.info("No students found. Add your first student above!")

    # --- PAGE: GENERATE FOLLOW-UP ---
    elif page == "Generate Follow-up":
        st.title("✍️ Generate Follow-up")
        
        import data
        import ai_helper
        
        students = data.get_students(user.id)
        if not students:
            st.warning("Please add students in the 'My Students' tab first.")
        else:
            student_options = {s['name']: s for s in students}
            selected_name = st.selectbox("Select Student", list(student_options.keys()))
            selected_student = student_options[selected_name]
            
            # --- INPUTS ---
            st.markdown("#### Message Setup")
            
            # Row 1: Quick Options
            r1_col1, r1_col2, r1_col3 = st.columns(3)
            category = r1_col1.selectbox("Category", ["General Update", "Behavior Issue", "Academic Performance", "Homework Update", "Exam Results"])
            tone = r1_col2.selectbox("Tone", ["Professional & Polite", "Encouraging & Warm", "Direct & Serious", "Concerned"])
            language = r1_col3.selectbox("Language", ["English", "Italian"])

            # Row 2: Specific Data
            remarks = st.text_input("Keywords / Facts for this Student", 
                placeholder="e.g., Math score 85%, failed to submit homework, very talkative today")

            # Row 3: Advanced/Custom
            with st.expander("Advanced: Custom Instructions (Optional)"):
                custom_instruction = st.text_area("Add specific guidance for the AI:", 
                    placeholder="e.g., 'Mention that the field trip is next week' or 'Be very brief.'",
                    height=80)

            # --- GENERATE ---
            if st.button("✨ Generate Draft", type="primary"):
                if remarks:
                    with st.spinner("AI is drafting..."):
                        draft = ai_helper.generate_followup_message(
                            selected_name, 
                            selected_student.get('grade'), 
                            remarks, 
                            custom_instruction,
                            category,
                            tone,
                            language
                        )
                        st.session_state.current_draft = draft
                else:
                    st.warning("Please enter at least some Keywords/Remarks.")
            
            # Show Draft & Save
            if "current_draft" in st.session_state:
                st.markdown("### 📝 Draft Message")
                final_content = st.text_area("Edit before saving:", value=st.session_state.current_draft, height=250)
                
                if st.button("💾 Save to History"):
                    # Record the full context
                    combined_notes = f"[{category}] {remarks} | Instr: {custom_instruction}"
                    data.save_followup(selected_student['id'], final_content, combined_notes)
                    st.success("Follow-up saved via Supabase!")
                    del st.session_state.current_draft # Clear state

    # --- PAGE: ANALYTICS ---
    elif page == "Student Analytics":
        st.title("📈 Student Insights")
        
        import data
        import ai_helper
        
        students = data.get_students(user.id)
        if not students:
            st.warning("No students available.")
        else:
            student_options = {s['name']: s for s in students}
            selected_name = st.selectbox("Select Student to Analyze", list(student_options.keys()))
            selected_student = student_options[selected_name]
            
            # Fetch history
            history = data.get_student_followups(selected_student['id'])
            
            if history:
                st.write(f"Found {len(history)} past follow-ups.")
                
                if st.button("🔍 Analyze Progress with AI"):
                    with st.spinner("Analyzing trends..."):
                        analysis = ai_helper.analyze_student_history(selected_name, history)
                        st.markdown(analysis)
                
                st.markdown("### Recent History")
                for item in history:
                    st.text_area(f"{item['created_at'].split('T')[0]}", value=item['content'], height=100, disabled=True)
            else:
                st.info("No history found for this student yet.")

if __name__ == "__main__":
    main()
