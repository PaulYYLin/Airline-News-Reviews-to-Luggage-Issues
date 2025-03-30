import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# read the data into the file
wtf = pd.read_csv("/Users/kellyw/Documents/GitHub/Airline-News-Reviews-to-Luggage-Issues/data/silver_airline_quality_reviews.csv")

# fix some values in the table... i swear to god
wtf['Overall_Rating'] = pd.to_numeric(wtf['Overall_Rating'], errors='coerce')

# sort the values so they are sorted in the dropdown menu
wtf_sorted = wtf.sort_values(by=['Airline Name'])

# put the unique values of that column into a list
airline_list = list(wtf_sorted['Airline Name'].unique())

# create a dictionary to store the values of each unique airline's average rating
airline_rating_dict = {
    "airline": [],
    "avg_rating": []
}

# calculate the average rating for each airline
for i in airline_list:
    avg_rate = np.round(np.mean(((wtf[wtf['Airline Name'] == i]['Overall_Rating']))), 6)
    airline_rating_dict['airline'].append(i)
    airline_rating_dict['avg_rating'].append(avg_rate)

# convert to a df
airline_rating_df = pd.DataFrame(airline_rating_dict)
airline_rating_df = airline_rating_df.sort_values(by=['avg_rating'], ascending=False).reset_index(drop=True)
total_num_airlines = len(airline_rating_dict['airline'])

# set up selection box

airline_select = st.selectbox('Select an airline', airline_list, 0)

# get the selected airline's average rating
airline_selected_avg = airline_rating_df[airline_rating_df['airline'] == airline_select]['avg_rating'].values[0]

# get the selected airline's ranking
airline_selected_ranking = airline_rating_df.loc[airline_rating_df['airline'] == airline_select].index[0] + 1

# get the selected airline's sentiment
airline_selected_sent = np.mean(wtf[wtf['Airline Name'] == airline_select]['sentiment_score'])

# set up the container to hold the first row of columns
with st.container(border=True):
    col1_1, col1_2, col1_3 = st.columns([1,1,1])
    with col1_1:
        st.header("Airline", divider='grey')
        st.title(airline_select)
    with col1_2:
        st.header("Average Rating", divider='grey')
        if airline_selected_avg >= 7:
            rating_colour = 'green'
        elif airline_selected_avg >= 4.5:
            rating_colour = 'orange'
        else:
            rating_colour = 'red'
        st.markdown(f"<h1 style='color:{rating_colour};'>{np.round(airline_selected_avg, 2)}</h1>", unsafe_allow_html=True)
    with col1_3:
        st.header("Ranking", divider='grey')
        st.markdown(f"<h1>{airline_selected_ranking}</h1> <p>out of {total_num_airlines}</p>", unsafe_allow_html=True)

# made a function to handle category avg ratings
def category_ratings(airline):
    list_cats = ["Seat Comfort", "Cabin Staff Service", "Food & Beverages", "Ground Service", "Inflight Entertainment",	"Wifi & Connectivity", "Value For Money"]
    list_cats_avg = list()
    for i in list_cats:
         sheesh = wtf[wtf['Airline Name'] == airline][i]
         avg = np.mean(sheesh)
         list_cats_avg.append(avg)
    cat_dict = {
         'Category': list_cats,
         'Avg_rating': list_cats_avg
    }
    cat_df = pd.DataFrame(cat_dict)
    cat_df = cat_df.sort_values(by=['Avg_rating'], ascending=False)
    print(cat_df.head())

    plot = alt.Chart(cat_df).mark_bar().encode(
         x='Category', 
         y='Avg Rating'
         )
    return plot

with st.container(border=True):
    col2_1, col2_2 = st.columns([2, 1])
    with col2_1:
        st.write('Category Ratings')
        st.altair_chart(category_ratings(airline_select))
    with col2_2:  
        if airline_selected_sent > 0.5:
            st.image("/Users/kellyw/Documents/GitHub/Airline-News-Reviews-to-Luggage-Issues/Dashboard/pages/assets/positive-sent.png")
        else:
            st.image("/Users/kellyw/Documents/GitHub/Airline-News-Reviews-to-Luggage-Issues/Dashboard/pages/assets/negative-sent.png")
