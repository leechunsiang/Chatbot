import streamlit as st
import google.generativeai as genai
import time
import uuid
import json
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="University Life Assistant",
    page_icon="🎓",
    layout="wide"
)

# Configure the Gemini API with the key from secrets.toml
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Custom CSS for better styling
st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.8rem; 
        margin-bottom: 1rem; 
        display: flex;
    }
    .chat-message.user {
        background-color: #F0F2F6;
    }
    .chat-message.bot {
        background-color: #E3F2FD;
    }
    .chat-message .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .chat-message .message {
        width: 80%;
    }
    .sample-questions {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 12px 0;
    }
    .sample-question-btn {
        background-color: #f0f0f0;
        border-radius: 16px;
        padding: 8px 16px;
        font-size: 14px;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .sample-question-btn:hover {
        background-color: #e0e0e0;
    }
    .chat-history-btn {
        text-align: left;
        padding: 10px;
        margin-bottom: 5px;
        border-radius: 5px;
        background-color: transparent;
        border: 1px solid #4b4b4b;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .chat-history-btn:hover {
        background-color: #333333;
    }
    .chat-history-btn.active {
        background-color: #444444;
        border-color: #7c7c7c;
    }
    .new-chat-btn {
        width: 100%;
        padding: 10px;
        margin-bottom: 15px;
        border-radius: 5px;
        background-color: #2e7d32;
        color: white;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .new-chat-btn:hover {
        background-color: #1b5e20;
    }
    .stTextInput>div>div>input {
        padding-right: 50px;
    }
</style>
""", unsafe_allow_html=True)

# University-specific context
UNIVERSITY_CONTEXT = """
You are an official UTAR (Universiti Tunku Abdul Rahman) virtual assistant. Your name is UTARian Guide.
Your purpose is to provide accurate, helpful information about all aspects of UTAR to students, 
prospective students, parents, and other stakeholders.

## ABOUT UTAR
- Full name: Universiti Tunku Abdul Rahman (UTAR)
- Founded: 2002 by the UTAR Education Foundation
- Motto: "Beyond Education, Inspiring Excellence"
- President: [Current President's Name]
- Type: Private university

## CAMPUSES
- Kampar Campus (Main): Jalan Universiti, Bandar Barat, 31900 Kampar, Perak, Malaysia
- Sungai Long Campus: Jalan Sungai Long, Bandar Sungai Long, 43000 Kajang, Selangor, Malaysia
- Campus facilities: [List key facilities like libraries, labs, sports facilities, etc.]

## ACADEMIC STRUCTURE
- Faculties and Centers:
  * Faculty of Accountancy and Management (FAM)
  * Faculty of Arts and Social Science (FAS)
  * Faculty of Business and Finance (FBF)
  * Faculty of Engineering and Green Technology (FEGT)
  * Faculty of Information and Communication Technology (FICT)
  * Faculty of Medicine and Health Sciences (FMHS)
  * Faculty of Science (FS)
  * Institute of Chinese Studies (ICS)
  * Centre for Foundation Studies (CFS)
  * [Add any other faculties/centers]

## ACADEMIC PROGRAMS
- Foundation Programs: [List key foundation programs]
- Undergraduate Programs: Over [X] degree programs across multiple disciplines
- Postgraduate Programs: Master's and PhD programs in [list key areas]
- Special Programs: [Any special academic initiatives]
- Academic Calendar: [Information about trimesters/semesters system]

## ADMISSIONS
- Entry Requirements:
  * Foundation: [Requirements]
  * Undergraduate: [Requirements]
  * Postgraduate: [Requirements]
- Application Process: [Brief description]
- Key Deadlines: [Any standard application deadlines]
- International Student Requirements: [Specific requirements]

## FEES AND FINANCIAL AID
- Tuition Fee Ranges:
  * Foundation: RM [range] per year
  * Undergraduate: RM [range] per year
  * Postgraduate: RM [range] per year
- Scholarships Available: [List main scholarships]
- Financial Aid Options: [List options]
- Payment Methods and Deadlines: [Brief info]

## STUDENT LIFE
- Student Organizations: Over [X] clubs and societies
- Major Annual Events: [List key events]
- Sports and Recreation: [Available sports and facilities]
- Student Services: [Key services like counseling, career services, etc.]
- Accommodation Options: [On-campus and nearby options]

## CAREER SERVICES
- Career Center: [Location and services]
- Internship Opportunities: [Key information]
- Industry Partnerships: [Major partners]
- Graduate Employment Rate: [Recent statistics if available]

## RESEARCH
- Research Centers: [List key research centers]
- Key Research Areas: [Main research focus areas]
- Notable Achievements: [Any significant research outcomes]

## INTERNATIONAL RELATIONS
- Partner Universities: Collaborations with over [X] universities worldwide
- Exchange Programs: [Brief description]
- International Student Support: [Available services]

## CONTACT INFORMATION
- General Inquiries: [Phone, email]
- Admissions Office: [Phone, email]
- Financial Aid Office: [Phone, email]
- International Office: [Phone, email]
- Website: https://www.utar.edu.my

Provide accurate information about the facilities of UTAR. For example, the location of the library, you 
should answer the Block in UTAR.

When answering questions, provide specific UTAR information whenever possible. If asked about topics 
requiring current or very specific data that you might not have (like current exact fees, recent policy 
changes, or specific course availability for upcoming terms), acknowledge the limitations, provide an estimated
assumption and suggest the user check the official UTAR website or contact the relevant department for the most up-to-date 
information.

If asked questions completely unrelated to UTAR or education or activities around UTAR, politely redirect the conversation to 
UTAR-related topics by mentioning you're specifically designed to provide information about UTAR.
"""

# File path for storing chat sessions
CHAT_STORAGE_PATH = "./.chat_sessions.json"

# Function to load chat sessions from file
def load_chat_sessions():
    if os.path.exists(CHAT_STORAGE_PATH):
        try:
            with open(CHAT_STORAGE_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading chat sessions: {e}")
            return {}
    return {}

# Function to save chat sessions to file
def save_chat_sessions():
    try:
        # Create a copy of chat sessions without the non-serializable elements
        serializable_sessions = {}
        for session_id, session_data in st.session_state.chat_sessions.items():
            serializable_sessions[session_id] = {
                'title': session_data['title'],
                'messages': session_data['messages'],
                'created_at': session_data.get('created_at', datetime.now().isoformat())
            }
        
        with open(CHAT_STORAGE_PATH, 'w') as f:
            json.dump(serializable_sessions, f)
    except Exception as e:
        st.error(f"Error saving chat sessions: {e}")

# Function to generate a descriptive title from conversation content
def generate_chat_title(user_message, ai_response):
    # First try to extract a title from the user message
    if len(user_message) <= 40:
        return user_message
    
    # If user message is too long, try to create a summarized title
    # Extract the first sentence or first 40 chars
    title = user_message.split('.')[0]
    if len(title) > 40:
        title = title[:37] + "..."
    
    return title

def initialize_session_state():
    # Load existing chat sessions
    if 'chat_sessions' not in st.session_state:
        st.session_state.chat_sessions = load_chat_sessions()
    
    # Initialize current session
    if 'current_session_id' not in st.session_state:
        # Use the most recent session if available, otherwise create new
        if st.session_state.chat_sessions:
            # Find the most recent session by created_at timestamp
            most_recent = max(st.session_state.chat_sessions.items(), 
                            key=lambda x: x[1].get('created_at', ''))
            st.session_state.current_session_id = most_recent[0]
        else:
            # Create a new session if none exist
            new_session_id = str(uuid.uuid4())
            st.session_state.current_session_id = new_session_id
            st.session_state.chat_sessions[new_session_id] = {
                'title': "New Conversation",
                'messages': [],
                'created_at': datetime.now().isoformat()
            }
    
    # Initialize Gemini model
    if 'gemini_model' not in st.session_state:
        st.session_state.gemini_model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    # Initialize Gemini chat for all sessions
    if 'gemini_chat' not in st.session_state:
        st.session_state.gemini_chat = {}
    
    # Ensure all sessions have a corresponding Gemini chat
    for session_id in st.session_state.chat_sessions:
        if session_id not in st.session_state.gemini_chat:
            st.session_state.gemini_chat[session_id] = st.session_state.gemini_model.start_chat(history=[])
            
            # Reconstruct chat history for Gemini from stored messages
            messages = st.session_state.chat_sessions[session_id]['messages']
            
            # First send the context
            st.session_state.gemini_chat[session_id].send_message(f"For this conversation, please note: {UNIVERSITY_CONTEXT}")
            
            # Then replay the conversation to maintain context
            for msg in messages:
                if msg["role"] == "user":
                    try:
                        st.session_state.gemini_chat[session_id].send_message(msg["content"])
                    except Exception:
                        # If an error occurs, we'll just continue with what we have
                        pass

# Function to create a new chat session
def create_new_chat():
    new_session_id = str(uuid.uuid4())
    st.session_state.current_session_id = new_session_id
    st.session_state.chat_sessions[new_session_id] = {
        'title': "New Conversation",
        'messages': [],
        'created_at': datetime.now().isoformat()
    }
    
    # Initialize a new Gemini chat for this session
    st.session_state.gemini_chat[new_session_id] = st.session_state.gemini_model.start_chat(history=[])
    st.session_state.gemini_chat[new_session_id].send_message(f"For this conversation, please note: {UNIVERSITY_CONTEXT}")
    
    # Save the updated chat sessions
    save_chat_sessions()
    st.rerun()

# Function to switch chat sessions
def switch_chat(session_id):
    st.session_state.current_session_id = session_id
    st.rerun()

# Function to generate response
def generate_response(prompt):
    session_id = st.session_state.current_session_id
    try:
        # Get response from Gemini
        response = st.session_state.gemini_chat[session_id].send_message(prompt)
        
        # Update the title if it's a new chat or has the default title
        if (len(st.session_state.chat_sessions[session_id]['messages']) == 0 or 
            st.session_state.chat_sessions[session_id]['title'] == "New Conversation"):
            # Generate a context-based title
            title = generate_chat_title(prompt, response.text)
            st.session_state.chat_sessions[session_id]['title'] = title
            # Save the updated title
            save_chat_sessions()
            
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

# Function to handle user input or sample questions
def handle_user_input(user_query):
    session_id = st.session_state.current_session_id
    
    # Add user message to chat
    st.session_state.chat_sessions[session_id]['messages'].append({"role": "user", "content": user_query})
    
    # Save after adding user message
    save_chat_sessions()
    
    # Generate assistant response
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        try:
            # Add typing effect
            message_placeholder.write("Thinking...")
            
            # Get response from Gemini
            response = generate_response(user_query)
            
            # Display final response
            message_placeholder.write(response)
            
            # Add assistant response to chat history
            st.session_state.chat_sessions[session_id]['messages'].append({"role": "assistant", "content": response})
            
            # Save after adding assistant message
            save_chat_sessions()
            
        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            message_placeholder.write(error_message)
            st.session_state.chat_sessions[session_id]['messages'].append({"role": "assistant", "content": error_message})
            save_chat_sessions()

# Initialize session state
initialize_session_state()

# Sidebar - Chat Sessions
with st.sidebar:
    st.title("💬 Chat Sessions")
    
    # New chat button
    if st.button("+ New Chat", key="new_chat", use_container_width=True):
        create_new_chat()
    
    # Display all chat sessions
    st.subheader("Recent Chats")
    
    # Sort sessions by most recent first
    sorted_sessions = sorted(
        st.session_state.chat_sessions.items(),
        key=lambda x: x[1].get('created_at', ''),
        reverse=True
    )
    
    for session_id, session_data in sorted_sessions:
        button_style = "active" if session_id == st.session_state.current_session_id else ""
        if st.button(session_data['title'], key=f"session_{session_id}", 
                    use_container_width=True, 
                    help=f"Switch to this conversation",
                    type="primary" if button_style == "active" else "secondary"):
            switch_chat(session_id)
    
    # About section at the bottom of the sidebar
    st.markdown("---")
    st.markdown("**UniGuide** - Your AI university assistant")
    st.markdown("v1.0 - Powered by Gemini Pro")

# Main chat area
st.title("🎓 University Life Assistant")
st.markdown("Your friendly guide to navigating university life. Ask me anything about academics, campus resources, student life, and more!")

# Display chat messages for current session
session_id = st.session_state.current_session_id
for message in st.session_state.chat_sessions[session_id]['messages']:
    if message["role"] == "user":
        with st.chat_message("user", avatar="👨‍🎓"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.write(message["content"])

# Sample questions above input box
st.markdown("---")
st.markdown("### Sample Questions")
col1, col2 = st.columns(2)

sample_questions = [
    "How do I choose the right major?",
    "What resources are available for mental health support?",
    "How can I get involved in extracurricular activities?",
    "What are some tips for managing academic workload?",
    "How do I apply for financial aid?"
]

with col1:
    for i in range(0, len(sample_questions), 2):
        if st.button(sample_questions[i], key=f"q_{i}", use_container_width=True):
            # Display user message in chat
            with st.chat_message("user", avatar="👨‍🎓"):
                st.write(sample_questions[i])
            
            # Handle the sample question
            handle_user_input(sample_questions[i])
            st.rerun()

with col2:
    for i in range(1, len(sample_questions), 2):
        if st.button(sample_questions[i], key=f"q_{i}", use_container_width=True):
            # Display user message in chat
            with st.chat_message("user", avatar="👨‍🎓"):
                st.write(sample_questions[i])
            
            # Handle the sample question
            handle_user_input(sample_questions[i])
            st.rerun()

# Get user input
user_query = st.chat_input("Ask about university life...")

# Process user input
if user_query:
    # Display user message in chat
    with st.chat_message("user", avatar="👨‍🎓"):
        st.write(user_query)
    
    # Handle user input
    handle_user_input(user_query)