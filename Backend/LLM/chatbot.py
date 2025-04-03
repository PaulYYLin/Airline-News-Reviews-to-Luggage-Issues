
from dotenv import load_dotenv
import os
import json
import requests

load_dotenv()

class Chatbot:
    def __init__(self):
        self.DATABRICKS_TOKEN = os.getenv('DATABRICKS_TOKEN')
        self.DATABRICKS_INSTANCE = os.getenv('DATABRICKS_INSTANCE')
        pass


    def chat_with_chatbot(self, prompt):
        try:
            data = {
            "dataframe_split":{
                "columns":[
                    "query"
                ],
                "data":[
                    [
                        prompt
                    ]
                ]
            }
            }

            headers = {"Context-Type": "text/json", "Authorization": f"Bearer {self.DATABRICKS_TOKEN}"}

            response = requests.post(
                url=f"{self.DATABRICKS_INSTANCE}/serving-endpoints/data608-llm-chatbot/invocations", json=data, headers=headers
            )

            result = json.dumps(response.json()['predictions']).encode().decode('unicode_escape')
            return result.strip('["]').replace('\\"', '"')
        except Exception as e:
            print(f"Error in chat_with_chatbot: {e}")
            return 'chatbot test successfully'
        
if __name__ == "__main__":
    chatbot = Chatbot()
    print(chatbot.chat_with_chatbot("What is the worst airline in the world?"))