"""
共用的樣式定義，可被所有頁面導入
"""

def load_css():
    return """
<style>
    /* ====================
       CSS VARIABLES - Color scheme and theme settings
    ==================== */
    :root {
        /* Background colors */
        --bg-primary: rgba(0, 0, 0, 0.9);
        --bg-secondary: rgba(30, 30, 30, 0.8);
        
        /* Text colors */
        --text-primary: rgba(255, 255, 255, 0.9);
        --text-secondary: rgba(220, 220, 220, 0.7);
        
        /* Accent and interactive elements */
        --accent-color: rgba(255, 215, 0, 0.7);
        --border-color: rgba(255, 255, 255, 0.2);
        --shadow-color: rgba(255, 255, 255, 0.3);
        
        /* UI Components */
        --input-bg: rgba(30, 30, 30, 0.7);
        --message-user-bg: rgba(70, 70, 70, 0.6);
        --message-bot-bg: rgba(50, 50, 50, 0.6);
        --button-bg: rgba(50, 50, 50, 0.5);
        --button-hover-bg: rgba(80, 80, 80, 0.7);
    }

    /* ====================
       GLOBAL STYLES - Base application appearance
    ==================== */
    .stApp {
        background: linear-gradient(90deg, #000000, #1a1a1a, #000000);
        color: var(--text-primary);
    }
    
    /* Hide Streamlit toolbar */
    div[data-testid="stToolbar"] {
        visibility: hidden;
    }

    /* ====================
       TYPOGRAPHY - Logo and text styling
    ==================== */
    .logo-text {
        font-size: 10rem;
        font-weight: 800;
        text-align: center;
        margin-top: 3rem;
        line-height: 1;
        -webkit-background-clip: text;
        text-stroke: 1px rgba(0, 0, 0, 0.5);
        -webkit-text-stroke: 1px rgba(0, 0, 0, 0.5);
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5), 0 0 20px;
        letter-spacing: 0.05em;
        opacity: 0.9;
        font-family: 'Arial Black', 'Helvetica Bold', sans-serif;
        color: var(--text-primary);
    }
    
    .logo-description {
        font-size: 2rem;
        font-weight: 300;
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        letter-spacing: 0.1em;
        font-family: 'Arial Black', 'Helvetica Bold', sans-serif;
    }
    
    /* ====================
       BUTTONS - Interactive elements styling
    ==================== */
    .button-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-bottom: 30px;
        width: 100%;
        flex-wrap: wrap;
    }
    
    .action-button {
        background-color: var(--button-bg);
        color: var(--text-primary);
        border-radius: 50px;
        padding: 10px 25px;
        border: 1px solid var(--border-color);
        margin: 10px;
        font-weight: 500;
        transition: all 0.3s;
        width: 200px;
        text-align: center;
        box-shadow: 0 0 10px var(--shadow-color);
        cursor: pointer;
    }
    
    .action-button:hover {
        background-color: var(--button-hover-bg);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    }
    
    .action-button:active {
        transform: translateY(1px);
    }
    
    /* ====================
       CHAT INTERFACE - Chat containers and messages
    ==================== */
    .chat-container {
        background: linear-gradient(to bottom, var(--bg-secondary), rgba(40, 40, 40, 0.6));
        border-radius: 15px;
        border: 2px solid var(--border-color);
        box-shadow: 0 0 15px var(--shadow-color);
        max-width: 800px;
        margin: 30px auto 20px auto;
        padding: 20px;
        height: 200px;
        overflow-y: auto;
    }
    
    /* User message bubble */
    .user-message {
        background-color: var(--message-user-bg);
        border-radius: 15px 15px 3px 15px;
        padding: 12px 18px;
        margin: 10px 0 10px auto;
        max-width: 75%;
        display: inline-block;
        float: right;
        clear: both;
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        animation: fadeIn 0.5s ease-in-out;
    }
    
    /* Bot message bubble */
    .bot-message {
        background-color: var(--message-bot-bg);
        border-radius: 15px 15px 15px 3px;
        padding: 12px 18px;
        margin: 10px 0;
        max-width: 75%;
        display: inline-block;
        float: left;
        clear: both;
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        animation: fadeIn 0.5s ease-in-out;
    }
    
    /* ====================
       FORM ELEMENTS - Input fields and controls
    ==================== */
    div[data-testid="stTextInput"] {
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
        background: linear-gradient(to bottom, var(--bg-secondary), rgba(40, 40, 40, 0.6));
        border-radius: 15px;
        border: 2px solid var(--border-color);
        padding: 15px 20px;
        margin-bottom: 30px;
    }
    
    div[data-testid="stTextInput"] input {
        padding: 10px 15px;
        border-radius: 25px;
        background-color: rgba(0, 0, 0, 0.83);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }
    
    /* Force Streamlit elements to use dark theme */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stMultiselect > div > div,
    .stSlider > div,
    .stDateInput > div > div {
        background-color: var(--input-bg) !important;
        color: var(--text-primary) !important;
        border-color: var(--border-color) !important;
    }
    
    /* ====================
       ANIMATIONS - Visual effects for dynamic elements
    ==================== */
    @keyframes gradientFlow {
        0%   { box-shadow: 0 0 5px rgba(255, 255, 255, 0.2); }
        50%  { box-shadow: 0 0 15px rgba(255, 255, 255, 0.4); }
        100% { box-shadow: 0 0 25px rgba(255, 255, 255, 0.6); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes glow {
        from { box-shadow: 0 0 5px rgba(255, 255, 255, 0.5); }
        to   { box-shadow: 0 0 15px rgba(255, 255, 255, 0.8); }
    }
    
    /* ====================
       RESPONSIVE DESIGN - Adaptations for different screen sizes
    ==================== */
    /* Tablets and smaller desktops */
    @media (max-width: 768px) {
        .logo-text {
            font-size: 5rem;
            margin-top: 2rem;
        }
        
        .logo-description {
            font-size: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        .button-container {
        display:block;
            flex-direction: row;
            justify-content: center;
            gap: 5px;
        }
        
        .action-button {
            width: 45%;
            margin: 5px;
            padding: 8px 15px;
            box-shadow: 0 0 10px rgba(255, 225, 225, 0.5);
            font-size: 0.9rem;
        }
        
        .chat-container {
            max-width: 95%;
            height: 300px;
        }
        
        div[data-testid="stTextInput"] {
            max-width: 95%;
        }
        
        .user-message, .bot-message {
            max-width: 85%;
        }
    }
    
    /* Mobile phones and small screens */
    @media (max-width: 480px) {
        .logo-text {
            font-size: 3rem;
            margin-top: 1rem;
        }
        
        .logo-description {
            font-size: 1rem;
            margin-bottom: 1rem;
        }
        
        .chat-container {
            height: 250px;
            padding: 10px;
        }
        
        /* Force horizontal button layout on small screens */
        .button-container {
            flex-direction: row !important; 
            display:block;
            justify-content: space-between !important;
            align-items: center !important;
            flex-wrap: nowrap !important; 
            gap: 10px;
            padding: 0 5px;
            width: 100%;
            max-width: 95%;
            margin: 0 auto 20px auto;
        }
        
        .action-button {
            width: calc(50% - 10px) !important;
            margin: 0 !important;
            padding: 8px 5px;
            font-size: 0.9rem;
            flex: 1 !important;
            min-width: 0;
        }
    }

    /* ====================
       DATA FRAME STYLING - Table and data display
    ==================== */
    [data-testid="stDataFrame"] {
        background-color: rgba(30, 30, 30, 0.7);
        border-radius: 10px;
        padding: 0px !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
    }

    [data-testid="stDataFrame"] table {
        border-collapse: collapse;
        width: 100%;
    }

    [data-testid="stDataFrame"] th {
        background-color: rgba(20, 20, 20, 0.9) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 12px 10px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    [data-testid="stDataFrame"] td {
        background-color: rgba(30, 30, 30, 0.6) !important;
        color: white !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 10px !important;
    }

    [data-testid="stDataFrame"] tr:hover td {
        background-color: rgba(50, 50, 50, 0.7) !important;
    }

    /* Custom progress bar styling for sentiment score */
    [data-testid="stDataFrame"] [data-testid="progress-bar-container"] {
        background-color: rgba(60, 60, 60, 0.4) !important;
        border-radius: 5px !important;
    }

    [data-testid="stDataFrame"] [data-testid="progress-bar"] {
        background: linear-gradient(90deg, 
            rgba(255, 0, 0, 0.8) 0%, 
            rgba(255, 165, 0, 0.8) 50%, 
            rgba(0, 220, 0, 0.8) 100%) !important;
    }

    /* Hide DataEditor toolbar */
    [data-testid="stDataFrame"] [data-testid="stDataFrameResizeIcon"],
    [data-testid="stDataFrame"] button {
        display: none !important;
    }
</style>
"""