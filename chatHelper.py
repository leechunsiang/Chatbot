import google.generativeai as genai
import streamlit as st

def initialize_gemini():
    """Initialize and configure the Gemini model"""
    try:
        # Configure the Gemini API
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # Create a generative model instance
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        return model
    except Exception as e:
        st.error(f"Error initializing Gemini: {str(e)}")
        return None

def get_university_context():
    """Return the university context for the chatbot"""
    return """
    You are a helpful assistant specializing in university life. Your purpose is to help students
    navigate various aspects of university experience, including academics, campus resources,
    student life, administrative procedures, housing, financial aid, career services, and health resources.
    
    Provide informative, accurate, and supportive responses. If you're unsure about specific details,
    acknowledge this and suggest where the student might find the information.
    """

def get_gemini_response(prompt, chat_history=[]):
    """Get response from Gemini API with chat history"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        chat = model.start_chat(history=chat_history)
        
        context = get_university_context()
        response = chat.send_message(f"{context}\n\nUser question: {prompt}")
        
        return response.text, chat.history
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}", chat_history