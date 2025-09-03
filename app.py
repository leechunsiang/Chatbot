import streamlit as st
import google.generativeai as genai
import time

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
</style>
""", unsafe_allow_html=True)

# University-specific context
UNIVERSITY_CONTEXT = """
You are a helpful assistant specializing in university life. Your name is UniGuide.
You provide guidance on various aspects of university experience, including:

1. Academic Programs & Courses: Information on majors, minors, course selection, prerequisites, etc.
2. Campus Resources: Libraries, study spaces, computer labs, academic support services
3. Student Life: Clubs, organizations, events, sports, recreation
4. Administrative Procedures: Registration, add/drop periods, graduation requirements
5. Housing & Accommodation: Dorms, off-campus housing, meal plans
6. Financial Aid: Scholarships, grants, loans, work-study opportunities
7. Career Services: Internships, job fairs, resume building, interview preparation
8. Health & Wellness: Medical services, counseling, fitness resources

When answering questions, be informative, accurate, and supportive. If you're unsure about 
university-specific details, acknowledge this and provide general guidance while suggesting 
the student consult official university resources for definitive answers.
"""

def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'gemini_model' not in st.session_state:
        st.session_state.gemini_model = genai.GenerativeModel('gemini-pro')
    if 'gemini_chat' not in st.session_state:
        st.session_state.gemini_chat = st.session_state.gemini_model.start_chat(
            history=[{"role": "system", "content": UNIVERSITY_CONTEXT}]
        )

initialize_session_state()

# Header
st.title("🎓 University Life Assistant")
st.markdown("Your friendly guide to navigating university life. Ask me anything about academics, campus resources, student life, and more!")

# Display chat messages
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user", avatar="👨‍🎓"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.write(message["content"])

# Get user input
user_query = st.chat_input("Ask about university life...")

# Process user input
if user_query:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Display user message in chat
    with st.chat_message("user", avatar="👨‍🎓"):
        st.write(user_query)
    
    # Generate assistant response
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        try:
            # Add typing effect
            full_response = ""
            message_placeholder.write("Thinking...")
            
            # Get response from Gemini
            response = st.session_state.gemini_chat.send_message(user_query)
            
            # Process response with typing effect
            full_response = response.text
            message_placeholder.write(full_response)
            
        except Exception as e:
            error_message = f"Sorry, I encountered an error: {str(e)}"
            message_placeholder.write(error_message)
            full_response = error_message
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Sidebar with helpful information
with st.sidebar:
    st.title("About UniGuide")
    st.markdown("""
    **UniGuide** is your AI assistant for all university-related questions. I can help with:
    
    - Academic planning and course selection
    - Campus resources and facilities
    - Student life and activities
    - Administrative processes
    - Housing and accommodation
    - Financial aid and scholarships
    - Career preparation
    - Health and wellness resources
    
    I'm still learning, so if I make a mistake, please let me know!
    """)
    
    # Add sample questions
    st.subheader("Sample Questions")
    sample_questions = [
        "How do I choose the right major?",
        "What resources are available for mental health support?",
        "How can I get involved in extracurricular activities?",
        "What are some tips for managing academic workload?",
        "How do I apply for financial aid?"
    ]
    
    for question in sample_questions:
        if st.button(question):
            st.session_state.messages.append({"role": "user", "content": question})
            st.rerun()