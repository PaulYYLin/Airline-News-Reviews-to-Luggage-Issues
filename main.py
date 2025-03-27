from DB.Postgres import Database
from Spiders.Reddit import Reddit
from LLM.model import llm_model



class Executor:
    def __init__(self):
        self.reddit = Reddit()
        self.db = Database()

    def query_data_from_db(self, table_name:str, limit=None):
        df = self.db.get_table_data(table_name, limit=limit)
        return df

    def trigger_reddit_spider(self, time_filter:str, limit:int, subreddit_name:str, sort:str):

        # Pass parameters to the executor
        self.reddit = Reddit()
        # reddit_posts = reddit.get_posts_from_subreddit(time_filter=time_filter, limit=limit, subreddit_name=subreddit_name, sort=sort)
        reddit_posts = self.reddit.get_historical_posts(subreddit_name=subreddit_name, limit=limit, sort=sort)
        num_posts = len(reddit_posts)

        self.db.store_data(reddit_posts, "reddit_testing_reviews")
    
        return {
            "message": f"Reddit posts saved to DB. Number of posts: {num_posts} with config: {time_filter}, {limit}, {subreddit_name}, {sort}"
        }


    def trigger_labeling(self, df):
        llm = llm_model()
        
        # 使用生成器逐批處理標註結果
        for batch_df in llm.review_labeling(df):
            self.db.store_data(batch_df, "labeling_values", primary_key='post_id')
            print(f"Batch labeling completed, saved {len(batch_df)} data")
        
        return {
            "message": "All labeling values saved to DB"
        }




if __name__ == "__main__":
    executor = Executor()
    executor.trigger_reddit_spider(time_filter="year", limit=1000, subreddit_name="flying", sort="hot")
    # df = executor.query_data_from_db(table_name="bronze_reddit_reviews", limit=1000)
    # print(df)
    # executor.trigger_labeling(df)
