import streamlit as st
from openai import OpenAI

# Configure OpenAI
api_key = st.secrets["openai"].get("api_key")
client = None
if api_key:
    client = OpenAI(api_key=api_key)

def generate_followup_message(student_name, grade, remarks, custom_instruction, category, tone, language="English"):
    """
    Generates a follow-up message using OpenAI (GPT-4o).
    """
    if not client:
        return "Error: OpenAI API Key not found in secrets."

    prompt = f"""
    You are a professional teacher's assistant.
    
    Target Language: {language} (IMPORTANT: Write the entire message in this language)
    
    Context:
    - Student Name: {student_name}
    - Grade: {grade}
    - Message Category: {category}
    - Desired Tone: {tone}
    
    Teacher's Keywords/Observations: "{remarks}"
    Teacher's Specific Instructions: "{custom_instruction}"
    
    Task: Write a complete follow-up message. 
    Use the Category and Tone to guide the structure and value. 
    Incorporate the specific Keywords/Observations naturally.
    Follow any Specific Instructions provided.
    
    Style Guide:
    - Detailed, narrative style.
    - Specific and personal.
    - Balanced between fun/engagement and learning milestones.
    
    Example of desired output style:
    "Vittoria had an excellent first session, settling in quickly and showing great enthusiasm. She demonstrated strong linguistic skills by repeating instructions and vocabulary in full sentences, which is a wonderful milestone for her age. She was particularly captivated by the 'Wobbly Tooth' story and engaged deeply with both the 'tooth fairy and Tooth' game and the prepositions activities. Her joy was evident throughout the class, and she successfully balanced having fun with active learning. It was a 'very good' first day that set a very positive tone for her future lessons."
    
    Do not add placeholders.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Using 4o-mini for speed/cost, or use "gpt-4o"
            messages=[
                {"role": "system", "content": "You are a professional teacher's assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating content: {str(e)}"

def analyze_student_history(student_name, followups):
    """
    Analyzes a list of past follow-ups to find trends using OpenAI.
    """
    if not client:
        return "Error: OpenAI API Key not found."
        
    if not followups:
        return "No sufficient history to analyze."

    # Combine past content
    history_text = "\n".join([f"- {f['created_at'].split('T')[0]}: {f['content']}" for f in followups[:10]])
    
    prompt = f"""
    Analyze the following progress updates for student '{student_name}'.
    Identify key trends in behavior, academic performance, and areas of improvement over time.
    
    History:
    {history_text}
    
    Output a bulleted summary of:
    1. Strengths
    2. Recurring Challenges
    3. Overall Trajectory (Improving/Declining/Stable)
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an insightful educational analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error analyzing history: {str(e)}"
