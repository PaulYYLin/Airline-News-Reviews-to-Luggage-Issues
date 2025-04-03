import os
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import json

load_dotenv()

XAI_API_KEY = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

class llm_model:
    def __init__(self):
        self.client = OpenAI(
            api_key=XAI_API_KEY,
            base_url="https://api.x.ai/v1",
        )

    def _labeling(self, review_text):
        completion = self.client.chat.completions.create(
            model="grok-2-latest",
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
            {
                "role": "system",
                "content": '''
                Label airline/airport posts with these fields in JSON format:
                    1. "aviation_related": 1 if related to airline/airport, else 0.
                    2. "luggage_issue": 1 if related to luggage issue, else 0.
                    3. "mentioned_airlines_routes": Flight routes with IATA codes.
                       Format: [origin, transfer1, transfer2,..., destination] or [origin, destination]
                    4. "responsible_airline": Airline responsible for luggage issue (ICAO code), else "unknown".
                    5. "incident_date": When issue occurred (YYYY-MM-DD if possible).
                return the json format only, no other text.

                Post: "{review_text}"
                '''
            },
            {   
                "role": "user",
                "content": review_text
            },
        ],
        )
        response = json.loads(completion.choices[0].message.content.replace("'", '"'))

        return response


    def review_labeling(self,df:pd.DataFrame):
        

        labeling_results = []
        

        for idx, row in df.iterrows():
            post_id = row['post_id']
            review_text = row['selftext']
            
            label_data = self._labeling(review_text)
            
            try:
                
                result_row = {
                    'post_id': post_id,
                    'aviation_related': int(label_data.get('aviation_related', 0)),
                    'luggage_issue': int(label_data.get('luggage_issue', 0)),
                    'mentioned_airlines_routes': label_data.get('mentioned_airlines_routes', None),
                    'responsible_airline': label_data.get('responsible_airline', None),
                }
                
                labeling_results.append(result_row)
                
                if len(labeling_results) >= 10:
                    temp_df = pd.DataFrame(labeling_results)
                    yield temp_df
                    labeling_results = [] 
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON for post_id {post_id}: {e}")
        
        if labeling_results:
            yield pd.DataFrame(labeling_results)

if __name__ == "__main__":
    response ='''
{
    "aviation_related": 1,
    "luggage_issue": 1,
    "mentioned_airlines_routes": [],
    "responsible_airline": "unknown",
    "incident_date": "2023-02-28",
}
'''
    json_data = json.loads(response)
    print(json_data, type(json_data))