import streamlit as st
from styles import load_css
import html
from utils.operation import API_client
import time

# Initialize API client
api_client = API_client()

# Configure page settings
st.set_page_config(
    page_title="ALI-HUB",
    page_icon="🛩️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None,
)

# Load custom CSS
st.markdown(load_css(), unsafe_allow_html=True)

# Main content with custom styling
st.markdown('<div class="logo-text">AI-HUB</div>', unsafe_allow_html=True)
st.markdown('<div class="logo-description">Aviation Information Hub</div>', unsafe_allow_html=True)

# Create a cached function to fetch reviews (runs in background with caching)
@st.cache_data(ttl=300)  # Cache with 5 minute (300 sec) time-to-live
def fetch_cached_reviews(n=5):
    """
    Fetch reviews with caching to prevent unnecessary API calls
    Returns a list of review strings or empty list on error
    """
    try:
        return api_client.get_last_n_reviews_for_ticker(n)
    except Exception as e:
        # Log error but don't display to avoid affecting UI
        print(f"Error fetching reviews: {e}")
        return []

# Initialize session state variables only once to avoid reruns
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    # Default values for immediate rendering
    st.session_state.reviews = [
        "I had a great time at WestJet lounge", 
        "The flight attendants were very helpful", 
        "Terrible service and delayed flight",
        "My luggage was damaged during the flight",
        "Security at YVR was extremely efficient"
    ]
    st.session_state.chat_history = []
    st.session_state.waiting_for_response = False
    st.session_state.user_submitted = False
    st.session_state.last_question = ""

# Attempt to get fresh reviews without blocking the UI
# This won't cause a rerun since it's a cached function
fresh_reviews = fetch_cached_reviews()
if fresh_reviews:
    # Only update if we have new data
    st.session_state.reviews = fresh_reviews

# Process reviews to ensure they're clean and non-empty
def prepare_ticker_text():
    """
    Process reviews and prepare ticker text
    Handles empty reviews and formats for display
    """
    clean_reviews = []
    for review in st.session_state.reviews:
        review_str = str(review).strip()
        if review_str:  # Only add non-empty strings
            # 转义每条评论内容，但不转义分隔符
            clean_reviews.append(html.escape(review_str))
            
    # Fallback for empty content
    if not clean_reviews:
        clean_reviews = ["Welcome to Aviation Information Hub"]
        
    # 返回已经带有HTML间隔的字符串，不需要再次转义
    return "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;✈️&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;".join(clean_reviews)

# Get ticker text without causing reruns
ticker_text = prepare_ticker_text()

# Calculate animation duration based on content length
animation_duration = max(20, len(ticker_text) / 10)

# Display ticker with animation
st.markdown(f"""
<div class="ticker-container">
    <div class="ticker-text">
        {ticker_text}
    </div>
</div>
<style>
    .ticker-container {{
        background-color: rgba(50, 50, 50, 0.7);
        color: white;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
        overflow: hidden;
        position: relative;
        height: 60px;
        display: flex;
        align-items: center;
        width: 100%;
    }}

    .ticker-text {{
        white-space: nowrap;
        animation: ticker {animation_duration}s linear infinite;
        font-size: 1.1rem;
        position: absolute;
        width: max-content;
        letter-spacing: 0.5px;
    }}
    
    @keyframes ticker {{
        0% {{ transform: translateX(100%); }}
        100% {{ transform: translateX(-100%); }}
    }}
</style>
""", unsafe_allow_html=True)

# Button container
st.markdown("""
<div class="button-container">
    <a href="dashboard" target="_self" style="text-decoration: none;">
        <button class="action-button">STATISTICIAN</button>
    </a>
    <a href="predict" target="_self" style="text-decoration: none;">
        <button class="action-button">PROPHET</button>
    </a>
</div>
""", unsafe_allow_html=True)

# Optimized chat display function to avoid reruns
def display_chat_history():
    """
    Display chat history with proper formatting
    Shows typing indicator when waiting for response
    """
    chat_html = '<div class="chat-container">'
    
    for message in st.session_state.chat_history:
        if message['type'] == 'user':
            chat_html += f'<div class="user-message">{html.escape(message["text"])}</div>'
        else:
            chat_html += f'<div class="bot-message">{html.escape(message["text"])}</div>'
    
    # Add loading indicator only when waiting for response
    if st.session_state.waiting_for_response:
        chat_html += '<div class="bot-message typing-indicator">Thinking<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span></div>'
    
    chat_html += '</div>'
    return chat_html

# Handle user input without triggering unnecessary reruns
def process_input():
    """
    Process user input when submitted
    Sets flags for asynchronous response handling
    """
    user_question = st.session_state.user_input
    if user_question and not st.session_state.waiting_for_response:
        # Save question for processing
        st.session_state.last_question = user_question
        # Add user message to chat history
        st.session_state.chat_history.append({'type': 'user', 'text': user_question})
        # Clear input field
        st.session_state.user_input = ""
        # Set waiting flag - this will show the typing indicator
        st.session_state.waiting_for_response = True
        # Set submission flag to trigger response processing
        st.session_state.user_submitted = True

# Create chat container once
chat_container = st.container()

# Display chat UI
with chat_container:
    # Render chat history
    st.markdown(display_chat_history(), unsafe_allow_html=True)

    # Add CSS for typing indicator - only added once
    st.markdown("""
    <style>
    .typing-indicator {
        background-color: #e6e6e6 !important;
        color: #555 !important;
    }
    .typing-indicator .dot {
        animation: typing 1.3s infinite;
        display: inline-block;
    }
    .typing-indicator .dot:nth-child(2) {
        animation-delay: 0.3s;
    }
    .typing-indicator .dot:nth-child(3) {
        animation-delay: 0.6s;
    }
    @keyframes typing {
        0%, 75%, 100% {
            transform: translate(0, 0.1em) scale(0.7);
            opacity: 0.4;
        }
        25% {
            transform: translate(0, -0.1em) scale(1);
            opacity: 1;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Process bot response only when needed
if st.session_state.user_submitted and st.session_state.waiting_for_response:
    # Reset submission flag immediately to prevent duplicate processing
    st.session_state.user_submitted = False
    
    try:
        # Get actual response from API
        bot_response = api_client.chat_with_chatbot(st.session_state.last_question)
        # Add real response to chat history
        st.session_state.chat_history.append({'type': 'bot', 'text': bot_response})
    except Exception as e:
        # Add error message to chat history
        st.session_state.chat_history.append({'type': 'bot', 'text': f"Sorry, I encountered an error: {str(e)}"})
    finally:
        # Reset waiting flag
        st.session_state.waiting_for_response = False
        # This is the only place we need a rerun - to update the UI after getting a response
        st.rerun()

# Input field - use on_change to trigger processing
user_question = st.text_input(
    "Chat input",
    placeholder="Ask Your Protector Anything...", 
    label_visibility="collapsed",
    key="user_input",
    on_change=process_input
)




