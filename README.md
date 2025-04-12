# Analysing Airline News, Reviews and Luggage Issues

### DATA 608 L02 (Winter 2025) – Project Final Draft

April 11, 2025

Prepared by

- Ferdinand (Fred) Catameo
- Cancan Chen
- David Errington
- Zwaiba Khan
- Paul Lin
- Kelly Wu

## Table of Contents

- [1. Introduction](#1-Introduction)
    - [1.1. Problem Statement](#11-Problem-Statement)
    - [1.2. Key Findings / Summary of Results](#12-Key-Findings--Summary-of-Results)
- [2. Data Engineering Lifecycle](#2-Data-Engineering-Lifecycle)
    - [2.0. Pipeline Diagram](#20-Pipeline-Diagram)
    - [2.1. Data Generation](#21-Data-Generation)
    - [2.2. Data Ingestion](#22-Data-Ingestion)
    - [2.3. Data Transformation](#23-Data-Transformation)
    - [2.4. Data Storage](#24-Data-Storage)
    - [2.5. Data Serving](#25-Data-Serving)
    - [2.6. Data Outputs: ML, Analytics](#26-Data-Outputs-ML-Analytics)
- [3. Limitations & Possible Next Steps](#3-Limitations-amp-Possible-Next-Steps)
- [4. Conclusion](#4-Conclusion)
- [5. Static Link to Project](#5-Static-Link-to-Project)
- [6. References](#6-References)

## 1. Introduction

### 1.1. Problem Statement

The internet contains a plethora of information and is often overwhelming for any one person to collect,
filter, and review on their own. This is especially true when it comes to seeking information about airlines
and airports. The converse is also true, with some hard-to-find information, such as luggage loss by
airlines. This project seeks to solve the problem of having to spend an insurmountable amount of time on
one’s own finding, collecting, and filtering information about luggage loss, airports and airlines. This
project aims to create a centralized dashboard that offers insights on luggage loss, service and quality of
airlines and airports using various sources. The goal is to help travellers make better informed decisions
about airlines and airports when travelling, so they can travel with peace of mind.

To solve this problem, we will collect data from various sources (i.e., social platforms, web search, etc.),
organize it into a data pipeline on a cloud platform (e.g., AWS), quantify it with machine learning methods
(e.g., NLP), and then present it with visualization tools (such as Streamlit) and also provide a
chatbot (fine-tune LLM) as the final result.

### 1.2. Key Findings / Summary of Results

- Of the total number of web scraped reviews from AirlineQuality.com, **roughly 42.33%** (9,966 out of 23,543) **gave an overall rating of 1/10**.
    
    ![image](https://hackmd.io/_uploads/BJfmzYSAye.png)

- Unsurprisingly, when looking at the number of reviews by seat type, the **highest number of reviews** were from travellers seated in **economy class** (20,107 out of 23,288; roughly 86.34%). The rest were seated in either business class, premium economy, or first class.

    ![image](https://hackmd.io/_uploads/rJWRGKBC1x.png)

- When considering the number of reviews by traveller type, the **majority of reviews** were from those **travelling for leisure** (17,927 out of 20,759; roughly 86.36%). Of those travelling for leisure, 7,561 were solo travellers, 5,577 were couples, and the rest (4,789) were families.

    ![image](https://hackmd.io/_uploads/HkXGmtHR1x.png)

- When we tried to calculate the Top 30 Airlines by Average Overall Rating, we saw that there were nine (9) airlines tied at number 1, with a score of 10 out of 10.

    ![image](https://hackmd.io/_uploads/HyTsmYSAye.png)

## 2. Data Engineering Lifecycle

### 2.0. Pipeline Diagram

![DATA608_Project_v4](https://hackmd.io/_uploads/H1aYgzGAke.png)

### 2.1. Data Generation

We did not generate our own data.

### 2.2. Data Ingestion

We had two major data sources:

1. AirlineQuality.com web scraping – [Source Code](https://github.com/PaulYYLin/Airline-News-Reviews-to-Luggage-Issues/blob/main/1_ReScrapeAirlineReviews_withImageUrls.ipynb)

    - Airline reviews were scraped using the Python library BeautifulSoup. We modified the original web scraping notebook from [Kaggle](https://www.kaggle.com/code/khushipitroda/airline-review-scrapping). We fixed a bug with the overall ratings wherein a '10' was being extracted as a '1'. The web scraping script loops through each of the airlines' review pages and extracts the most recent 100 reviews data, storing the extracted records in a CSV file. Originally, the script took about 40 minutes and extracted roughly 23,000+ reviews.
    - To be able to do an incremental ingestion, we modified the script to check for the last ingested date from the database table and extract only new reviews for each airline that were posted on or after our last ingested date. This reduced the web scraping time down to just 5 to 17 minutes, extracting on average roughly 59 new reviews each run instead of the previous entire full load.
    
2. Reddit.com API airline reviews extraction

    - We also extracted aviation-related reviews from the Reddit.com API.
    
    
### 2.3. Data Transformation

#### 2.3.1. Data Cleaning and Preprocessing – [Source Code](https://github.com/PaulYYLin/Airline-News-Reviews-to-Luggage-Issues/blob/main/2_DataPreprocessing.ipynb)

The scraped Airline Quality reviews data underwent the following data cleaning and preprocessing steps:

1. `"Unnamed: 0"` CSV column was renamed as `"RowId"`.
    ```python!
    #Rename "Unnamed: 0" to "RowId"
    df = df_raw.copy()
    df.rename(columns={"Unnamed: 0": "RowId"}, inplace=True)
    ```
    
2. The string format of `"Review Date"` and `"Date Flown"` CSV columns were converted to the proper date format `YYYY-MM-DD` and their data types were converted to datetime.
    ```python!
    #Format and Convert Dates
    df['Review Date'] = pd.to_datetime(df['Review Date'], format="mixed")
    df['Date Flown'] = pd.to_datetime(df['Date Flown'], format="mixed")
    ```
3. Key columns needed were checked for any nulls.

    - No missing values were found.

4. `'Overall_Rating'` column value `'n'` was replaced with a null, and the data type was converted to float.
    ```python!
    df['Overall_Rating'] = df['Overall_Rating'].replace('n', np.nan).astype(float)
    ```

5. A unique ID was generated for each ingested review record, based on the hash of key columns: `'Airline Name'`, `'Review Date'`, and `'Review Title'`. These were used as the primary key in our database table, and to ensure no duplicate reviews were inserted during incremental ingestion.
    ```python!
    def generate_hash(row):
        value = f"{row['Airline Name']}|{row['Review_Title']}|{row['Review Date']}"
        return hashlib.sha256(value.encode()).hexdigest()
    df['Id'] = df.apply(generate_hash, axis=1)
    ```

#### 2.3.2. Sentiment Score ML Labeling – [Source Code](https://github.com/PaulYYLin/Airline-News-Reviews-to-Luggage-Issues/blob/main/3_Sentiment_Labeling.ipynb)

After data preprocessing, the review texts were then sent through a machine learning model to generate sentiment labels and scores for positive, negative, or neutral sentiments. We used the [cardiffnlp/twitter-roberta-base-sentiment-latest](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest) model from Hugging Face.
    
#### 2.3.3 "Lost Luggage" Topic ML Labeling – [Source Code](https://github.com/PaulYYLin/Airline-News-Reviews-to-Luggage-Issues/blob/main/3a_LostLuggage_Labeling.ipynb)

The review texts were then classified by a machine learning model to label if the topic was about 'Lost luggage'. The texts and the topic label were converted to vector embeddings using [thenlper/gte-small](https://huggingface.co/thenlper/gte-small) from Hugging Face. Finally, a cosine similarity score was computed for the review's semantic similarity to the topic.

### 2.4. Data Storage

#### 2.4.1. AWS PostgreSQL Relational Database

1. Airline Quality Reviews Tables – [Source Code](https://github.com/PaulYYLin/Airline-News-Reviews-to-Luggage-Issues/blob/main/4_IngestAirlineQualityReviews.ipynb)
    
    - The preprocessed and classified Airline Quality reviews were first inserted into a staging table       `"bronze_airline_quality_reviews"` in the project         PostgreSQL relational database. The staged `"bronze_airline_quality_reviews"` records were then inserted into a `"silver_airline_quality_reviews"` table. During the insertion, records were checked by ID to see if they did not exist yet in the table to ensure no duplicates were inserted.
    
2. Reddit Airline Reviews Tables
    
    - The preprocessed and labelled Reddit airline reviews were inserted into a `bronze_reddit_airline_reviews` table.

        ![image](https://hackmd.io/_uploads/B1EaXGMA1e.png)

#### 2.4.2. AWS Databricks Volume and Vector Database Table

1. Upload processed CSV file to Databricks volume - [Source Code](https://github.com/PaulYYLin/Airline-News-Reviews-to-Luggage-Issues/blob/main/5_UploadToDatabricksVolume.ipynb)
 
    - A copy of the preprocessed and ML-labeled ingested reviews CSV file was uploaded to AWS Databricks volume using the [Databricks files API](https://docs.databricks.com/api/workspace/files/upload).
    ![image](https://hackmd.io/_uploads/rJevZMfCyg.png)

2. Ingest CSV file to Databricks delta table.
    
    - The CSV file records were ingested into the Databricks delta table. Note that the change data capture setting was (and should be) enabled on the table.
    ```python!
    import pandas as pd

    df_airline_quality_reviews = pd.read_csv('/Volumes/workspace/data608/data608_volume/silver_airline_quality_reviews.csv')
    ```
    
    ```sql!
    %sql
    INSERT INTO workspace.data608.silver_airline_quality_reviews
    (
      airline_review_id, 
      review_text_data,
      `Airline Name`, 
      `Overall_Rating`, 
      `Review_Title`, 
      `Review Date`, 
      `Verified`, 
      `Review`, 
      `Aircraft`, 
      `Type Of Traveller`, 
      `Seat Type`, 
      `Route`, 
      `Date Flown`, 
      `Seat Comfort`, 
      `Cabin Staff Service`, 
      `Food & Beverages`, 
      `Ground Service`, 
      `Inflight Entertainment`, 
      `Wifi & Connectivity`, 
      `Value For Money`, 
      `Recommended`, 
      `sentiment_label`, 
      `is_lost_luggage_flag`,
      `Top Review Image Url`,
      created_by
    )
    SELECT `Id` AS airline_review_id,
      `Review` AS review_text_data,
      `Airline Name`, 
      cast(ifnull(`Overall_Rating`, 0) as INT) AS `Overall_Rating`, 
      `Review_Title`,
      `Review Date`,
      cast(`Verified` AS BOOLEAN) AS `Verified`, 
      `Review`, 
      `Aircraft`, 
      `Type Of Traveller`, 
      `Seat Type`, 
      `Route`,
      `Date Flown`,
      cast(`Seat Comfort` as INT) AS `Seat Comfort`, 
      cast(`Cabin Staff Service` as INT) AS `Cabin Staff Service`, 
      cast(`Food & Beverages` as INT) AS `Food & Beverages`, 
      cast(`Ground Service` as INT) AS `Ground Service`, 
      cast(`Inflight Entertainment` as INT) AS `Inflight Entertainment`, 
      cast(`Wifi & Connectivity` as INT) AS `Wifi & Connectivity`, 
      cast(`Value For Money` as INT) AS `Value For Money`, 
      cast(CASE WHEN `Recommended` = 'yes' THEN True ELSE False END AS BOOLEAN) AS `Recommended`, 
      `sentiment_label`,
      cast(False AS BOOLEAN) AS is_lost_luggage_flag,
      `Top Review Image Url`,     
      'data pipeline' AS created_by
    FROM vw_df_airline_quality_reviews
    ```
    
3. Synchronize the Databricks vector search index on the table.
    
    - After records were inserted, the vector search index that was created on the delta table needed to be synced using the created vector search endpoint compute. This could be done either via the UI or the code below:
    
        ```python!
        from databricks.vector_search.client import VectorSearchClient

        client = VectorSearchClient(workspace_url="https://dbc-0480908b-048c.cloud.databricks.com", personal_access_token=dbutils.secrets.get(scope="data608_secret_scope", key="data608_pat"))

        client.create_delta_sync_index(
            endpoint_name="data608_vector_search",
            index_name="workspace.data608.silver_airline_quality_reviews_vsi",
            primary_key="airline_review_id",
            source_table_name="workspace.data608.silver_airline_quality_reviews",
            pipeline_type="TRIGGERED"
            embedding_dimension=1024,
            embedding_vector_column="__db_review_text_data_vector",
            embedding_source_column="review_text_data",
            embedding_model_endpoint_name="databricks-bge-large-en",
            sync_computed_embeddings=True
        )    
        ```
    
4. Define the Retriever function from the Vector Store.
    
    - Here, we defined the retriever of the chatbot. The built-in, Databricks BGE Large (En) embedding model was used to convert the review text data to vector embeddings. We also defined the vector store database, vector search endpoint compute, and created a vector search index.
    
    ```python!
    from databricks.vector_search.client import VectorSearchClient
    from langchain_community.vectorstores import DatabricksVectorSearch
    from langchain_community.embeddings import DatabricksEmbeddings

    embedding_model = DatabricksEmbeddings(endpoint="databricks-bge-large-en")

    def get_retriever(persist_dir: str = None):
        os.environ["DATABRICKS_HOST"] = host

        #Get the vector search index
        vsc = VectorSearchClient(workspace_url=host, personal_access_token=os.environ["DATABRICKS_TOKEN"])

        #Specify vector search endpoint and index
        vs_index = vsc.get_index(
            endpoint_name=VECTOR_SEARCH_ENDPOINT_NAME,
            index_name=index_name
        )

        #Create the retriever
        vectorstore = DatabricksVectorSearch(
            vs_index, text_column="review_text_data", embedding=embedding_model
        )

        return vectorstore.as_retriever()    
    ```
    
5. Define the RAG `chat_model`, system prompt template using Langchain.
    
    - We used the built-in Databricks/DBRX Instruct chat model. The system prompt template for the chatbot was also defined below, setting the "personality" and expected response format of the chatbot.
    
    ```python!
    from langchain.chains import RetrievalQA
    from langchain.prompts import PromptTemplate
    from langchain_community.chat_models import ChatDatabricks

    chat_model = ChatDatabricks(endpoint="databricks-dbrx-instruct", max_tokens = 200)

    TEMPLATE = """You are an assistant for an airlines passenger reviews search and analysis chatbot. If the question is not related to one of these topics, kindly decline to answer. If you don't know the answer, just say that you don't know, don't try to make up an answer. If the question appears to be for an airline you don't have data on, say so.  Keep the answer as concise as possible.  Provide all answers only in English.
    Use the following pieces of context to answer the question at the end:
    {context}
    Question: {question}
    Answer:
    """
    prompt = PromptTemplate(template=TEMPLATE, input_variables=["context", "question"])

    chain = RetrievalQA.from_chain_type(
        llm=chat_model,
        chain_type="stuff",
        retriever=get_retriever(),
        chain_type_kwargs={"prompt": prompt}
    )    
    ```
    
6. Register `chat_model` to Databricks model registry.
    
    - The chatbot model needed to be registered to the Databricks model registry, so that an API serving endpoint could be created.
    
    ```python!
    from mlflow.models import infer_signature
    import mlflow
    import langchain

    mlflow.set_registry_uri("databricks-uc")
    model_name = "workspace.data608.llm_chatbot_model"

    with mlflow.start_run(run_name="llm_chatbot_run") as run:
        signature = infer_signature(question, answer)
        model_info = mlflow.langchain.log_model(
            chain,
            loader_fn=get_retriever,
            artifact_path="chain",
            registered_model_name=model_name,
            pip_requirements=[
                "mlflow==" + mlflow.__version__,
                "langchain==" + langchain.__version__,
                "databricks-vectorsearch",
            ],
            input_example=question,
            signature=signature
        )    
    ```
    
7. Enable Databricks RAG Chatbot Model serving endpoint.
    
    - Ensure the serving endpoint of the created Retrieval Augmented Generation LLM Chatbot Model was enabled to be accessible by end-users such as the Streamlit dashboard using the invocation URL and the secret Databricks token created. Just like any API, end-users can post a question and the RAG chatbot will generate and return a response answer augmented by the airline reviews data stored in the vector store database, utilizing the vector search index for quick retrieval.
    - Here is a sample Python script to post a question to the chatbot API and get a response back:
    
        ```python!
        import json
        import requests
        data = {
           "dataframe_split":{
              "columns":[
                 "query"
              ],
              "data":[
                 [
                    "Which airport has the worst reviews?"
                 ]
              ]
           }
        }

        headers = {"Context-Type": "text/json", "Authorization": f"Bearer {DATABRICKS_TOKEN}"}

        response = requests.post(
            url=f"{DATABRICKS_INSTANCE}/serving-endpoints/data608-llm-chatbot/invocations", json=data, headers=headers
        )

        result = json.dumps(response.json()['predictions']).encode().decode('unicode_escape')
        print(result.strip('["]').replace('\\"', '"'))    
        ```

### 2.5. Data Serving

#### 2.5.1. Backend Deployment & API

We implemented each pipelines' connection with [FastAPI](https://fastapi.tiangolo.com/#installation) package to create the endpoint for frontend. We also employed a Docker image to wrap up the backend executor and deployed it into Amazon EC2 as our server.

#### 2.5.2. Frontend

With [Streamlit](https://streamlit.io/) and [Streamlit Community](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app) as our frontend and server respectively, we integrated the Chatbot, Dashboard and Model. We used button and even chat area to trigger the end point from the backend to get data and responses. We accelerated the render speed with [LRU Cache](https://leetcode.com/problems/lru-cache/description/) to provide a better user experience.

### 2.6. Data Outputs: ML, Analytics

Our final output was a Streamlit-based visual product that can be accessed via PC or mobile app. The first phase of the product includes three main interfaces: an Analytics Dashboard, a Prediction Page, and a Chatbot Page. Below are the details:

1. **Analytics Dashboard**: The Analytics Dashboard, which is built on historical data, allows users to view key metrics such as the total number of reviews, the number of baggage-related complaints, and more. Users can also explore trends in sentiment-based reviews over time, as well as rankings of airlines based on the number of reviews. Overall, this dashboard provides users with a clear and comprehensive overview of airline-related baggage reviews.
![image](https://hackmd.io/_uploads/HyuisGIR1x.jpg)
![image](https://hackmd.io/_uploads/Sybniz8Cyx.jpg)
![image](https://hackmd.io/_uploads/ryq3jzIAyl.jpg)


2. **Prediction**: The Prediction Page is powered by two trained machine learning models: one uses a linear regression algorithm to predict the overall rating, and the other employs a random forest model to predict the sentiment label.
    ```python!
    import streamlit as st
    import joblib
    import pandas as pd

    @st.cache_resource
    def load_models():
        rating_model = joblib.load('model.joblib')
        sentiment_model = joblib.load('rf_model.joblib')
        return rating_model, sentiment_model

    rating_model, sentiment_model = load_models()

    features = ['Seat_Comfort', 'Cabin_Staff_Service', 'Food_Beverages', 
                'Ground_Service', 'Wifi_Connectivity', 'Value_For_Money']
    ```
    ![image](https://hackmd.io/_uploads/BJvuof8AJe.jpg)
    ![image](https://hackmd.io/_uploads/SJkFizICke.jpg)
    ![image](https://hackmd.io/_uploads/HkKKjfUC1l.jpg)

3. **RAG LLM Chatbot**: This page not only allows users to ask the chatbot questions related to the reviews, but also enables real-time viewing of review-related information.
![image](https://hackmd.io/_uploads/r1PwjM8Ckg.jpg)

## 3. Limitations & Possible Next Steps

1. EC2 vs. Lambdas

    - We are running all our Python data ingestion, data transformation, database insertion scripts on our project EC2 on a daily schedule or on-demand. We wanted to run the Python scripts on a chain of Lambdas, so that it would be serverless with less cost on-demand and could scale dynamically. The current incremental data volume ingested and processed is still manageable by our current project EC2.
    - We were able to use zipped file layers to install the needed Pyscopg2 modules needed to query from and insert to our PostgreSQL database. We also started working on more zipped file layers and a Docker image to install the machine learning libraries needed but needed more time to build and test the Lambdas. This is the  reason why we fell back to our original EC2 data pipeline.
    
2. PostgreSQL RDS vs DynamoDB or Aurora RDS

    - We also wanted to go serverless with DynamoDB for better scalability and less cost on-demand for our data storage. However, we already had a lot of work in place on our PostgreSQL relational database and wanted to focus more instead on quickly building the dashboard, that we opted to keep our PostgreSQL database. The team did not want to switch anymore to NoSQL in accessing our data storage. The serverless Aurora relational database option would have been more ideal for us, but it was unfortunately not available on the AWS Learner Lab offerings.
    - To date, we have used up only **$19.5** of our $50 AWS Learner Lab credits hosting our project PostgreSQL database, which is not bad cost-wise.

    <img src=https://hackmd.io/_uploads/rkUgbfGRyl.png  alt="drawing" width="50%" style="display: block; margin: 0 auto"/>
    
3. AWS Databricks Free Trial Limit

    - The AWS Databricks free trial is only for 14 days with a $40 credit.
    - We hoped to look into alternative vector store database options available out there that are less costly or free of charge and could run on a local machine or perhaps an EC2 or VM. Some alternative options available included ChromaDB or FAISS. We also hoped to research on hosting our local RAG LLM Chatbot without the Databricks model serving endpoint.

4. Databricks Vector Search Index Compute Cost

    - Databricks by itself has serverless compute. As long as one does not utilize premium features, such as enterprise-grade security or the vector search index, cost will be relatively affordable on-demand per usage. However, we needed the vector search index for our RAG LLM chatbot. The vector search index was performant and allowed for near real-time data update synchronization, but it costs $0.28 (USD) per hour once activated. It cannot be disabled temporarily when not in use.

5. Naive to Agentic RAG Chatbot Upgrade

    - The current RAG chatbot we have in place was a naive-RAG. It is limited to answering questions regarding our airline reviews data. Research into making the chatbot "agentic" could make it capable of calling an API such as https://aviationstack.com/ for recent airline flight information or do mathematical computations to further augment its response and answer more complex questions beyond our airline reviews data.

## 4. Conclusion

Made for the everday traveller, our project shares insights about airline reviews and lost luggage collected from two websites, AirlineQuality.com and Reddit.com. Using a combination of webscraping and an API to access two different sources of data, we were able to put together a comprehensive dataset to share these insights. Together our data highlighted some general key findings, such as, reviews were most significantly contributed by those flying economy class compared to other seat types. This indicates that these reviews come from everyday travellers, such as ourselves. 

Since the data collected for this project came from two different websites, some preprocessing was required to help us merge the data collected. This preprocessing included changing formats, removing any null values, and generating a unique ID for each review to ensure a clean and consistent data. Additionally, we conducted sentiment analysis and topic modelling to:

1. Determine the sentiment value of each review, and
2. Identify which reviews were specifically about lost luggage.

Once the preprocessing was complete, the data was stored in an AWS PostgreSQL Relational Database and uploaded to AWS Databricks volume for the chatbot. For the chatbot, we used the built-in Databricks/DBRX Instruct chat model and the Databricks BGE Large (En) embedding model to help us create the vector store database, and vector search index for fast data retrieval. Finally, we used Streamlit as our frontend to present our data via a dashboard, sentiment prediction page and to host our chatbot using buttons to trigger the end point from the backend to get data and responses. We also accelerated the render speed with [LRU Cache](https://leetcode.com/problems/lru-cache/description/) for a better user experience.

Looking ahead, there are a few things we would like to explore if we were to revisit this project. These include hosting on a chain of lambdas, or using DynamoDB instead to reduce costs and allow our application to scale dynamically as more reviews are added (since reviews are never-ending!). We would also take more time to develop a more 'agentic' chatbot to answer more complex questions and multi-turn interactions. 

We did encounter some limitations, especially related to the costs of Databricks and the Databricks Vector Search Index Compute which limited our ability to run our chatbot continously. Another limitiation was our inability to access certain airline review data directly from airlines themselves, as it was often protected or very costly to attain. As a result, we had to rely on data that was posted publicly online. This may have introduced some bias in our dataset, but increasing the dataset size and diversity could help mitigate this. However, this brings us to our next limitation, which was time. With more time, we would have liked to collect more data from additional sources, to help us build an even more comprehensive picture of traveller experiences!

The goal of our project was to create a tool that collected and analyzed user experiences and lost luggage incidents and to share that information with other travellers. We hope our project serves as a starting point for future efforts to harness the internet’s vast and scattered information, specifically on airlines so it is easier for everyday people to explore, understand, and make decisions from it.

## 5. Static Link to Project

GitHub Repository: <br>        https://github.com/PaulYYLin/Airline-News-Reviews-to-Luggage-Issues

## 6. References

1. *Build High-Quality RAG Apps with Mosaic AI Agent Framework and Agent Evaluation, Model Serving, and Vector Search | Databricks.* (n.d.). Databricks. https://www.databricks.com/resources/demos/tutorials/data-science-and-ai/lakehouse-ai-deploy-your-llm-chatbot

2. Pitroda, K., & Bhojani, J. (2023, July 27). *SkyRatings: Unleashing 23K+ airline reviews!* Kaggle. https://www.kaggle.com/datasets/khushipitroda/airline-reviews/data
