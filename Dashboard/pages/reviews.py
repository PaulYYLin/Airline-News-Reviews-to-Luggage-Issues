import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import os

file_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "silver_airline_quality_reviews.csv")

# Read the CSV file
wtf = pd.read_csv(file_path)

wtf = pd.read_csv(file_path)

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
         x=alt.X('Category', sort='-y', axis=alt.Axis(labelAngle=0, labelFontSize=7, labelOverlap=False)),
         y=alt.Y('Avg_rating', title='Average Rating'),
         color= alt.Color('Category').scale(scheme='darkblue')
         )
    return plot

# made something to handle sentiment for now?

def overall_sent(airline):
    all_sents = wtf[wtf['Airline Name'] == airline]['sentiment_label']
    total_reviews = len(all_sents)
    neutrals = 0
    positives = 0
    negatives = 0

    for sent in all_sents:
        if sent == 'positive':
            positives+=1
        elif sent == 'negative':
            negatives+=1
        elif sent == 'netural':
            neutrals+=1

    pos_percentage = positives/total_reviews if total_reviews > 0 else 0
    neg_percentage = negatives/total_reviews if total_reviews > 0 else 0
    neu_percentage = neutrals/total_reviews if total_reviews > 0 else 0

    sentiment_percent = {
        "positive": pos_percentage,
        "neutral": neu_percentage,
        "negative": neg_percentage,
    }
    
    sentiment_sorted = sorted(sentiment_percent, key=sentiment_percent.get, reverse=True) # sorts in descending order (highest to lowest)
    # handle ties by going positive > neutral > negative 
    return sentiment_sorted[0]

pos_img_path = os.path.join(os.path.dirname(__file__), ".", "assets", "positive-sent.png")
neg_img_path = os.path.join(os.path.dirname(__file__), ".", "assets", "negative-sent.png")

# making the second row
with st.container(border=True):
    col2_1, col2_2 = st.columns([3, 1])
    with col2_1:
        st.write('Category Ratings')
        st.altair_chart(category_ratings(airline_select))
    with col2_2:    
        st.header("Overall Review Sentiment")
        if overall_sent(airline_select) == 'positive':
            st.image(pos_img_path, width=120)
        elif overall_sent(airline_select) == 'negative':
            st.image(neg_img_path, width=120)
        elif overall_sent(airline_select) == 'neutral':
            st.header('neutral')
