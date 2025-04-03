from Spiders.Helpers import Helpers
import datetime
import dateutil.parser as dtparser
import pandas as pd
import numpy as np
import hashlib
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import os



class Airquality:

    def __init__(self, days_before_today:int=3):
        self.helpers = Helpers()
        self.skytrax_urls= ["https://skytraxratings.com/airlines?types=full_service"]

        self.ub_date, self.lb_date= None, '2025-01-01'
        # if give, cast date info else get the current date
        self.ub_date = dtparser.parse(self.ub_date) if self.ub_date is not None else datetime.datetime.today()

        #  if given, cast date info else  set zero
        self.lb_date = dtparser.parse(self.lb_date) if self.lb_date is not None else datetime.datetime.today()-datetime.timedelta(days=3)

        self.embedding_model = SentenceTransformer("thenlper/gte-small")
        self.sentiment_model = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
        
    
    def get_reviews(self):
        if not os.path.exists("reviews.csv"):
            reviews_df = pd.DataFrame()
            for url in self.skytrax_urls:

                airline_names= self.helpers.get_airline_names(url=url)
                print(str(len(airline_names))+ " airlines are found for the following link: " + url )
                # create directory for each skytrax link with search info

            for airline_name in airline_names:
                reviews = self.helpers.get_reviews(airline_name= airline_name,ub_date=self.ub_date,lb_date=self.lb_date)
                if reviews is not None:
                    reviews = pd.DataFrame(reviews)
                    reviews_df = pd.concat([reviews_df, reviews])
            reviews_df = reviews_df.drop_duplicates(subset=['Airline Name', 'Review_Title']).to_csv("reviews.csv", index=False)

        else:
            reviews_df = pd.read_csv("reviews.csv")
        
        try:
            reviews_df = self._preprocess_reviews(reviews_df)
            reviews_df['Id'] = reviews_df.apply(self._generate_hash, axis=1)
            reviews_df = self._sentiment_labeling(reviews_df)
            reviews_df = self._loss_luggage_labeling(reviews_df)
            os.remove("reviews.csv")
            return reviews_df
        except Exception as e:
            print(f"Error in labeling: {e}")
            return None
    
    def _preprocess_reviews(self, reviews_df:pd.DataFrame):
        reviews_df['Review Date'] = pd.to_datetime(reviews_df['Review Date'], format="mixed")
        reviews_df['Date Flown'] = pd.to_datetime(reviews_df['Date Flown'], format="mixed")
        reviews_df = reviews_df.replace(r'^\s+$', np.nan, regex=True)
        reviews_df = reviews_df.dropna()
        reviews_df['Overall_Rating'] = reviews_df['Overall_Rating'].replace('n', np.nan).astype(float)
        return reviews_df

    def _generate_hash(self, row):
        value = f"{row['Airline Name']}|{row['Review_Title']}|{row['Review Date']}|"
        return hashlib.sha256(value.encode()).hexdigest()
    
    def _sentiment_labeling(self, reviews_df:pd.DataFrame):
        
        reviews_df['sentiment'] = self.sentiment_model(reviews_df['Review_Title'])
        review_texts = reviews_df['Review_Title'].fillna("").astype(str).tolist()
        batch_size = 32
        all_results = []

        for i in range(0, len(review_texts), batch_size):
            batch = review_texts[i:i + batch_size]
            try:
                batch_results = self.sentiment_model(
                    batch,
                    truncation=True,
                    max_length=512
                )
                all_results.extend(batch_results)
            except Exception as e:
                print(f"Error in batch {i}-{i+batch_size}: {e}")
                all_results.extend([{'label': 'ERROR', 'score': 0.0} for _ in batch])
        sentiments_df = pd.DataFrame(all_results)
        sentiments_df.columns = ['sentiment_label', 'sentiment_scores']
        reviews_df = reviews_df.join(sentiments_df, how='left')

        return reviews_df
    
    def _loss_luggage_labeling(self, reviews_df:pd.DataFrame):
        tmp = reviews_df[['Id','Review']].copy()
        tmp['review_gte_small_embeddings']  = self.embedding_model.encode(tmp['Review']).to_list()
        
        verified_text = 'lost luggage mishandled baggage'
        verified_text_embedding = self.embedding_model.encode(verified_text).to_list()

        cosine_sim = np.dot(tmp['review_gte_small_embeddings'], verified_text_embedding) / (np.linalg.norm(tmp['review_gte_small_embeddings']) * np.linalg.norm(verified_text_embedding))
        tmp[f'lost_luggage_cosim'] = cosine_sim

        category_threshold = 0.84252
        tmp[f'is_lost_luggage_flag'] = tmp[f'lost_luggage_cosim'] >= category_threshold
        
        reviews_df = reviews_df.merge(tmp[['Id','is_lost_luggage_flag']], on='Id', how='left')
        return reviews_df
    

if __name__ == "__main__":
    airquality = Airquality(days_before_today=1)
    reviews_df = airquality.get_reviews()
    print(reviews_df)