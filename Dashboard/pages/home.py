import streamlit as st
from styles import load_css

# Set dark theme and wider layout
st.set_page_config(
    page_title="ALR-LP",
    page_icon="🛩️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None,
)

# Load custom CSS
st.markdown(load_css(), unsafe_allow_html=True)

# Main content with custom styling
st.markdown('<div class="logo-text">ALR-LP</div>', unsafe_allow_html=True)
st.markdown('<div class="logo-description">Aviation Live Reviews - Luggage Protector</div>', unsafe_allow_html=True)

# Button container - now directly below the logo with less space
st.markdown("""
<div class="button-container">
    <a href="/realtime" style="text-decoration: none;">
        <button class="action-button">REALTIME</button>
    </a>
    <button class="action-button">HISTORICAL</button>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# 定義處理輸入的回調函數
def process_input():
    if st.session_state.user_input and not st.session_state.submitted:
        # 獲取用戶輸入
        user_question = st.session_state.user_input
        
        # 標記已提交，防止無限循環
        st.session_state.submitted = True
        
        # 添加用戶消息到 session state
        st.session_state.chat_history.append({'type': 'user', 'text': user_question})
        
        # 添加機器人響應到 session state
        bot_response = "You can find it on the moon."  # 替換為實際的響應邏輯
        st.session_state.chat_history.append({'type': 'bot', 'text': bot_response})
        
        # 通過設置 session state 中的標記來清空輸入框
        st.session_state.user_input = ""

# Create an outer container
outer_container = st.container()

with outer_container:
    # Create chat container that will hold all messages
    chat_container = st.container()
    
    # Create the chat interface with message history
    with chat_container:
        chat_html = '<div class="chat-container">'
        
        # Add previous chat history
        for message in st.session_state.chat_history:
            if message['type'] == 'user':
                chat_html += f'<div class="user-message">{message["text"]}</div>'
            else:
                chat_html += f'<div class="bot-message">{message["text"]}</div>'
        
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    
    # Input field placed below the chat container with on_change callback
    user_question = st.text_input("", placeholder="Ask Your Protector Anything...", 
                                 label_visibility="collapsed", max_chars=100,
                                 key="user_input",
                                 on_change=process_input)
    
    # 如果已提交，在新的執行中重置標記
    if st.session_state.submitted:
        st.session_state.submitted = False
        st.rerun()




