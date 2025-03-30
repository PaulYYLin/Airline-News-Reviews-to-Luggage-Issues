import streamlit as st
from new_home_styles import load_css

st.set_page_config(
    page_title="Airline Information Hub",
    page_icon="🛩️",
    initial_sidebar_state="collapsed",
    layout="wide"
)

# set background to plane image
st.markdown(load_css(), unsafe_allow_html=True)

# title container
st.markdown("""
<div class="landing-div">
    <h1 class="landing-title">AIRLINE INFORMATION HUB</h1>                   
</div>
""", unsafe_allow_html=True)

# grid to show the three different sections
col1, col2 = st.columns([.7,.3])

with col1:
    st.markdown("""
    <div class="custom-grid-container">
        <div class="custom-grid-row">
            <div class="custom-column">
                <p>Left Column</p>
            </div>
            <div class="custom-column">
                <h1 class="column-heading">Airline Reputation & Reviews</h1>
            </div>
            <div class="custom-column">
                <button>Button</button>
            </div>
            <div class="custom-column-full-span">
                <p class="subtitle">See with other travelers are saying!</p>
            </div>
        </div>
        <div class="custom-grid-row">
            <div class="custom-column">
                <p>Left Column</p>
            </div>
            <div class="custom-column">
                <h1 class="column-heading">Lost Luggage Statistics</h1>
            </div>
            <div class="custom-column">
                <button>Button</button>
            </div>
            <div class="custom-column-full-span">
                <p class="subtitle">How likely are you to lose your bag?</p>
            </div>
        </div>
        <div class="custom-grid-row">
            <div class="custom-column">
                <p>Left Column</p>
            </div>
            <div class="custom-column">
                <h1 class="column-heading">Compare Airlines</h1>
            </div>
            <div class="custom-column">
                <button>Button</button>
            </div>
            <div class="custom-column-full-span">
                <p class="subtitle">Find the airline that suits your needs!</p>
            </div>
        </div>
    </div>
    """,unsafe_allow_html=True)

# chatbot, copy and pasted from home.py, some stylings are copied over
with col2:
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
