import streamlit as st

# --- page setup ---

home_page = st.Page(
    page = "home.py",
    title = "Home",
    icon = "🏠",
    default = True
)

reviews_page = st.Page(
    page = "reviews.py",
    title = "REVIEWS",
    icon = "📖",
)

lost_luggage_page = st.Page(
    page= "lost_luggage.py",
    title= "LOST LUGGAGE",
    icon = "🧳",
)

### -- setup navigation --
ng = st.navigation(
    {
        "Home": [home_page],
        "Airline Statistics": [reviews_page],
        "Lost Luggage  Information": [lost_luggage_page]
    })

ng.run()