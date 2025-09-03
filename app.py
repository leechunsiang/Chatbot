import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from functions import map_role, fetch_gemini_response

# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="University Life Chatbot",
    page_icon="🎓",  # University-themed emoji
    layout="centered",  # Keeps it neat
)

API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=API_KEY)

# Initialize Gemini model with system instruction for university life focus
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',  # Use a lightweight model for quick responses; swap to 'gemini-pro' if needed
    system_instruction="You are a helpful university life advisor. Answer questions about university life, including academics, campus activities, student services, dorm life, extracurriculars, career advice, and mental health support. Be friendly, informative, and concise. If the question is off-topic, politely redirect to university-related topics."
)

# Initialize chat session in Streamlit if not already present
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Display the chatbot's title
st.title("🎓 University Life Chatbot")

# Show a brief description
st.markdown("Ask me anything about university life—academics, campus tips, student life, and more!")

# Display chat history
for msg in st.session_state.chat_session.history:
    with st.chat_message(map_role(msg.role)):
        st.markdown(msg.parts[0].text)

# Input field for user's message
user_input = st.chat_input("Ask about university life...")

if user_input:
    # Display user's message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get Gemini's response
    gemini_response = fetch_gemini_response(user_input)
    
    # Display assistant's response
    with st.chat_message("assistant"):
        st.markdown(gemini_response)
    
    # Update chat history (Gemini handles context automatically)
    st.session_state.chat_session.history.append(genai.types.ContentType(role="user", parts=[genai.types.PartType(text=user_input)]))
    st.session_state.chat_session.history.append(genai.types.ContentType(role="model", parts=[genai.types.PartType(text=gemini_response)]))