import streamlit as st
import joblib
import pandas as pd
from styles import load_css

# Set page configuration
st.set_page_config(
    page_title="Airline Rating Prediction",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# Load custom CSS
st.markdown(load_css(), unsafe_allow_html=True)


# Add custom CSS for prediction page
st.markdown("""
<style>
    /* Force dark theme regardless of browser settings */
    .stApp {
        background-color: #121212 !important;
        background-image: none !important;
    }
    
    /* Ensure all Streamlit elements use dark background */
    div.stTextInput, div.stTextArea, div.stButton, div.stSelectbox, div.stMultiselect {
        background-color: rgba(30, 30, 30, 0.7) !important;
    }
    
    div[data-testid="stForm"] {
        background-color: rgba(30, 30, 30, 0.7) !important;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Prediction page specific styling */
    .prediction-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 20px;
        color: rgba(255, 255, 255, 0.9);
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        letter-spacing: 0.05em;
    }
    
    .header-description {
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.7);
        max-width: 800px;
        margin: 0 auto 20px auto;
        text-align: center;
        line-height: 1.5;
    }
    
    
    /* Prediction button styling */
    .stButton > button {
        background: linear-gradient(90deg, rgba(138, 43, 226, 0.7), rgba(148, 53, 236, 0.7)) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 30px !important;
        padding: 5px 25px !important;
        font-weight: 600 !important;
        box-shadow: 0 0 10px rgba(138, 43, 226, 0.4) !important;
        transition: all 0.3s !important;
    }

    .st-emotion-cache-ocsh0s {
        background-color: black !important;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, rgba(148, 53, 236, 0.8), rgba(158, 63, 246, 0.8)) !important;
        box-shadow: 0 0 15px rgba(138, 43, 226, 0.6) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Navigation link */
    .nav-link {
        display: inline-block;
        margin-top: 10px;
        color: rgba(220, 220, 220, 0.9);
        text-decoration: none;
        font-size: 0.9rem;
        transition: all 0.3s;
        text-align: center;
    }
    
    .nav-link:hover {
        color: rgba(255, 255, 255, 1);
        text-decoration: underline;
    }
    
    /* Add space between result and form */
    .result-section {
        margin-bottom: 30px;
    }
    
    /* Override Streamlit text input */
    div[data-testid="stTextInput"] > div > div > input {
        background-color: rgba(50, 50, 50, 0.8) !important;
        color: white !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Override Streamlit select box */
    div[data-testid="stSelectbox"] > div > div > div {
        background-color: rgba(50, 50, 50, 0.8) !important;
        color: white !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Force all text to be light colored */
    .stMarkdown, .stText, p, span, label, .stSelectbox, .stSlider {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* Ensure dark background for sidebar */
    .css-1d391kg, .css-12oz5g7 {
        background-color: rgba(20, 20, 20, 0.9) !important;
    }
</style>
""", unsafe_allow_html=True)

# Load the models
@st.cache_resource
def load_models():
    rating_model = joblib.load('Frontend/static/model.joblib')
    sentiment_model = joblib.load('Frontend/static/rf_model.joblib')
    return rating_model, sentiment_model

rating_model, sentiment_model = load_models()

# Define the features
features = ['Seat_Comfort', 'Cabin_Staff_Service', 'Food_Beverages', 
            'Ground_Service', 'Wifi_Connectivity', 'Value_For_Money']

# Header section
st.markdown('<div class="logo-text">Experience Predictor</div>', unsafe_allow_html=True)
st.markdown('<div class="header-description">Predict the overall rating and passenger sentiment based on your experience metrics. Move the sliders to input your ratings for different aspects of your flight experience.</div>', unsafe_allow_html=True)


st.markdown("""
<div class="button-container">
    <a href="/" target="_self" style="text-decoration: none;">
        <button class="action-button"> ChatBot </button>
    </a>
    <a href="dashboard" target="_self" style="text-decoration: none;">
        <button class="action-button">Dashboard</button>
    </a>
</div>
""", unsafe_allow_html=True)
# Initialize session state for storing inputs and results
if 'inputs' not in st.session_state:
    st.session_state.inputs = {feature: 3 for feature in features}
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'rating_pred' not in st.session_state:
    st.session_state.rating_pred = None
if 'sentiment_pred' not in st.session_state:
    st.session_state.sentiment_pred = None

# Create a function to update state on submit
def handle_submit():
    # Create DataFrame from inputs
    input_df = pd.DataFrame([st.session_state.inputs])
    
    # Make predictions
    st.session_state.rating_pred = rating_model.predict(input_df)[0]
    st.session_state.sentiment_pred = sentiment_model.predict(input_df)[0]
    st.session_state.submitted = True

# Display prediction results if submitted
if st.session_state.submitted:
    st.markdown('<div class="result-section">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: rgba(255, 255, 255, 0.9);'>Prediction Results</h2>", unsafe_allow_html=True)
    
    # Create columns for results
    col1, col2 = st.columns(2)
    
    # Rating prediction
    with col1:
        st.markdown("<h3 style='text-align: center; color: rgba(255, 255, 255, 0.85);'>Overall Rating</h3>", unsafe_allow_html=True)
        rating_emoji = "⭐" * int(round(st.session_state.rating_pred))
        st.markdown(f"<h1 style='text-align: center; color: #FFD700;'>{st.session_state.rating_pred:.1f}/10</h1>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 1.5rem;'>{rating_emoji}</div>", unsafe_allow_html=True)
        
        # Colorful progress bar
        progress_color = "rgba(138, 43, 226, 0.8)" if st.session_state.rating_pred >= 5 else "rgba(255, 99, 71, 0.8)"
        st.markdown(f"""
        <div style="margin-top: 10px; background: rgba(50, 50, 50, 0.4); border-radius: 5px; height: 10px; width: 100%;">
            <div style="background: {progress_color}; width: {st.session_state.rating_pred*10}%; height: 10px; border-radius: 5px;"></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Sentiment prediction
    with col2:
        st.markdown("<h3 style='text-align: center; color: rgba(255, 255, 255, 0.85);'>Passenger Sentiment</h3>", unsafe_allow_html=True)
        
        sentiment_map = {
            "negative": ("Negative", "🔴", "#ff4b4b"),
            "neutral": ("Neutral", "🟡", "#ffd166"),
            "positive": ("Positive", "🟢", "#06d6a0")
        }
        
        sentiment_label, sentiment_icon, sentiment_color = sentiment_map.get(st.session_state.sentiment_pred, ("Unknown", "❓", "#808080"))
        
        st.markdown(f"""
        <h1 style='text-align: center; color: {sentiment_color};'>{sentiment_label}</h1>
        <div style='text-align: center; font-size: 3rem;'>{sentiment_icon}</div>
        """, unsafe_allow_html=True)
    
    # Interpretation of results
    st.markdown("<h3 style='text-align: center; color: rgba(255, 255, 255, 0.85); margin-top: 20px;'>Interpretation</h3>", unsafe_allow_html=True)
    
    # Provide personalized insight based on the prediction
    if st.session_state.rating_pred >= 7.5:
        insight = "Excellent! Your ratings indicate a highly satisfying flight experience that would likely result in positive reviews."
    elif st.session_state.rating_pred >= 5:
        insight = "Good. Your ratings suggest a decent flight experience with some room for improvement."
    else:
        insight = "Below average. These ratings indicate a less than satisfactory experience that might lead to negative reviews."
    
    st.markdown(f"<p style='text-align: center; color: rgba(255, 255, 255, 0.7);'>{insight}</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Add a separator between results and form
    st.markdown("<hr style='margin: 30px 0; border-color: rgba(255, 255, 255, 0.1);'>", unsafe_allow_html=True)

# Create input form with improved styling
with st.form("prediction_form"):
    st.markdown("<h3 style='text-align: center; color: rgba(255, 255, 255, 0.9);'>Rate Your Flight Experience</h3>", unsafe_allow_html=True)
    
    # Add specific CSS to ensure button is properly centered between sliders
    st.markdown("""
    <style>
        /* Center submit button container */
        div[data-testid="stFormSubmitButton"] {
            display: flex !important;
            justify-content: center !important;
            margin: 30px auto 10px auto !important;
            width: 100% !important;
        }
        
        /* Style for submit button to ensure it's centered and wider */
        div[data-testid="stFormSubmitButton"] button {
            min-width: 220px !important;
            margin: 0 auto !important;
            padding: 10px 20px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Create two columns for sliders (first row)
    col1, col2 = st.columns(2)
    
    with col1:
        # Left column sliders
        st.session_state.inputs['Seat_Comfort'] = st.slider(
            label="Seat Comfort",
            min_value=1,
            max_value=5,
            value=st.session_state.inputs['Seat_Comfort'],
            help="Rate the comfort of your seat from 1 (worst) to 5 (best)"
        )
        
        st.session_state.inputs['Cabin_Staff_Service'] = st.slider(
            label="Cabin Staff Service",
            min_value=1,
            max_value=5,
            value=st.session_state.inputs['Cabin_Staff_Service'],
            help="Rate the cabin staff service from 1 (worst) to 5 (best)"
        )
        
        st.session_state.inputs['Food_Beverages'] = st.slider(
            label="Food & Beverages",
            min_value=1,
            max_value=5,
            value=st.session_state.inputs['Food_Beverages'],
            help="Rate the food and beverages from 1 (worst) to 5 (best)"
        )
    
    with col2:
        # Right column sliders
        st.session_state.inputs['Ground_Service'] = st.slider(
            label="Ground Service",
            min_value=1,
            max_value=5,
            value=st.session_state.inputs['Ground_Service'],
            help="Rate the ground service from 1 (worst) to 5 (best)"
        )
        
        st.session_state.inputs['Wifi_Connectivity'] = st.slider(
            label="WiFi & Connectivity",
            min_value=1,
            max_value=5,
            value=st.session_state.inputs['Wifi_Connectivity'],
            help="Rate the WiFi and connectivity from 1 (worst) to 5 (best)"
        )
        
        st.session_state.inputs['Value_For_Money'] = st.slider(
            label="Value For Money",
            min_value=1,
            max_value=5,
            value=st.session_state.inputs['Value_For_Money'],
            help="Rate the value for money from 1 (worst) to 5 (best)"
        )
    
    # Add a comment to explain the purpose of the button (English annotation)
    st.markdown("<p style='text-align: center; color: rgba(180, 180, 180, 0.7); font-style: italic; margin-top: 20px;'>Click the button below to generate your flight experience rating prediction</p>", unsafe_allow_html=True)
    
    # Submit button will automatically be centered due to our CSS
    submitted = st.form_submit_button("Generate Predictions", on_click=handle_submit)

# Add navigation link






