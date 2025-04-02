# import streamlit as st
# import joblib
# import pandas as pd

# # Load the models
# @st.cache_resource
# def load_models():
#     rating_model = joblib.load('utils/model.joblib')
#     sentiment_model = joblib.load('utils/rf_model.joblib')
#     return rating_model, sentiment_model

# rating_model, sentiment_model = load_models()

# # Define the features
# features = ['Seat_Comfort', 'Cabin_Staff_Service', 'Food_Beverages', 
#             'Ground_Service', 'Wifi_Connectivity', 'Value_For_Money']

# # Streamlit app
# st.title("Airline Passenger Review Prediction")
# st.write("This app predicts the overall rating and sentiment based on passenger experience metrics.")

# # Create input form
# with st.form("prediction_form"):
#     st.header("Input Passenger Experience Metrics")
    
#     # Create sliders for each feature
#     inputs = {}
#     cols = st.columns(2)
#     for i, feature in enumerate(features):
#         with cols[i % 2]:
#             inputs[feature] = st.slider(
#                 label=feature.replace('_', ' '),
#                 min_value=1,
#                 max_value=5,
#                 value=5,
#                 help=f"Rate the {feature.replace('_', ' ')} from 1 (worst) to 5 (best)"
#             )
    
#     submitted = st.form_submit_button("Predict")

# if submitted:
#     # Create DataFrame from inputs
#     input_df = pd.DataFrame([inputs])
    
#     # Make predictions
#     rating_pred = rating_model.predict(input_df)[0]
#     sentiment_pred = sentiment_model.predict(input_df)[0]
    
#     # Display results
#     st.success("Predictions generated successfully!")
    
#     st.subheader("Results")
    
#     # Rating prediction
#     # st.metric(label="Predicted Overall Rating", value=f"{rating_pred:.1f}")

#     st.markdown("### Overall Rating")
#     rating_emoji = "⭐" * int(round(rating_pred))
#     st.markdown(f"<h1 style='text-align: center; color: #FFD700;'>{rating_pred:.1f}/10 {rating_emoji}</h1>", 
#                 unsafe_allow_html=True)
#     st.progress(rating_pred/10)
    
#     # st.metric(label="Predicted Sentiment", value=sentiment_pred)
#     st.markdown("### Passenger Sentiment")
#     sentiment_map = {
#         "negative": ("Negative", "🔴", "#ff4b4b"),
#         "neutral": ("Neutral", "🟡", "#ffd166"),
#         "positive": ("Positive", "🟢", "#06d6a0")
#     }
#     sentiment_label, sentiment_icon, sentiment_color = sentiment_map.get(sentiment_pred, ("Unknown", "❓", "#808080"))
    
#     st.markdown(
#         f"""<h1 style='text-align: center; color: {sentiment_color};'>
#         {sentiment_label} {sentiment_icon}
#         </h1>""", 
#         unsafe_allow_html=True
#     )

