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

When answering questions, provide specific UTAR information whenever possible. If asked about topics 
requiring current or very specific data that you might not have (like current exact fees, recent policy 
changes, or specific course availability for upcoming terms), acknowledge the limitations and suggest 
the user check the official UTAR website or contact the relevant department for the most up-to-date 
information.

If asked questions completely unrelated to UTAR or education, politely redirect the conversation to 
UTAR-related topics by mentioning you're specifically designed to provide information about UTAR.
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