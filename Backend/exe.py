from DB.Postgres import Database
from Spiders.Reddit import Reddit
from LLM.chatbot import Chatbot
from Spiders.Airquality import Airquality
import time
import pandas as pd
import datetime
from io import StringIO
import threading

class Executor:
    # Global instance that can be reused across requests
    _instance = None
    _initialized = False
    
    @classmethod
    def get_instance(cls):
        """Return a singleton instance to reuse data across requests"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self.reddit = Reddit()
        self.db = Database()
        # Initialize cache for dashboard data
        self.dashboard_cache = {}
        self.cache_timestamp = time.time()
        self.cache_expiry = 300  # 5 minutes
        
        # Only perform initialization once
        if not Executor._initialized:
            # Start background thread for preloading data
            self._start_preload_thread()
            Executor._initialized = True

    def _start_preload_thread(self):
        """Start background thread to preload essential data"""
        def preload_data():
            try:
                print("Backend preloading started")
                # Load main data
                main_data = self._load_main_data()
                if main_data is not None:
                    # Prepare "All Airlines" data
                    self.get_all_dashboard_data("All Airlines")
                    # Get airlines list
                    airlines = self.get_airlines()
                    # Preload data for the first airline if available
                    if airlines and len(airlines) > 0:
                        self.get_all_dashboard_data(airlines[0])
                print("Backend preloading completed")
            except Exception as e:
                print(f"Error in backend preloading: {e}")
        
        # Start preloading in a background thread
        preload_thread = threading.Thread(target=preload_data)
        preload_thread.daemon = True
        preload_thread.start()


    def trigger_realtime_reddit_spider(self, time_filter:str, limit:int, subreddit_name:str, sort:str):

        # Pass parameters to the executor
        self.reddit = Reddit()
        # reddit_posts = reddit.get_posts_from_subreddit(time_filter=time_filter, limit=limit, subreddit_name=subreddit_name, sort=sort)
        reddit_posts = self.reddit.get_search_posts(subreddit_name=subreddit_name, time_filter=time_filter, limit=limit, sort=sort)
        num_posts = len(reddit_posts)

        self.db.store_data(reddit_posts, "bronze_reddit_reviews", primary_key="post_id")
        print(f"Reddit posts saved to DB. Number of posts: {num_posts} with config: {time_filter}, {limit}, {subreddit_name}, {sort}")
        return num_posts
    
    def trigger_airquality_spider(self, days_before_today:int):
        airquality = Airquality(days_before_today=days_before_today)
        reviews_df = airquality.get_reviews()
        self.db.store_data(reviews_df, "silver_airline_quality_reviews", primary_key="Id")
        # After updating the data, invalidate the cache
        self.dashboard_cache = {}
        self.cache_timestamp = time.time()
        # Restart preloading thread to refresh cache with new data
        self._start_preload_thread()
        return reviews_df



# For Frontend =======================================================================

    def query_data_from_db(self, table_name:str, limit=None):
        df = self.db.get_table_data(table_name, limit=limit)
        return df
    
    # For Home Page =======================================================================
    def chat_with_chatbot(self, prompt):
        chatbot = Chatbot()
        return chatbot.chat_with_chatbot(prompt)
    

    def get_last_n_reviews_for_ticker(self, n:int):
        df = self.db.get_table_data("bronze_reddit_reviews", limit=n)
        ticker_information = []
        if df is not None and not df.empty:
            # Process each row to format time + review
            for _, row in df.iterrows():
                # Convert timestamp to readable format (assuming created_utc is a timestamp)
                try:
                    # If it's a Unix timestamp
                    time_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(int(row['created_utc'])))
                except:
                    # If it's already a string or other format
                    time_str = str(row['created_utc'])
                
                # Get the review text
                review_text = str(row['title']).strip()
                
                # Truncate long reviews
                if len(review_text) > 300:
                    review_text = review_text[:300] + "..."
                    
                # Format as "Time: Review text"
                formatted_review = f"{time_str}: {review_text}"
                ticker_information.append(formatted_review)
        
        return ticker_information

    # Dashboard data endpoints =======================================================================
    def _should_reset_cache(self):
        """Check if cache should be reset based on expiry time"""
        current_time = time.time()
        if current_time - self.cache_timestamp > self.cache_expiry:
            self.cache_timestamp = current_time
            # Clear cache
            self.dashboard_cache = {}
            # Start preloading in background after cache reset
            self._start_preload_thread()
            return True
        return False
    
    def _load_main_data(self):
        """Load main data table for dashboard operations"""
        cache_key = "main_data"
        
        # Check if we need to reset cache
        self._should_reset_cache()
        
        # Return cached data if available
        if cache_key in self.dashboard_cache:
            return self.dashboard_cache[cache_key]
        
        try:
            print("Loading main data from database...")
            start_time = time.time()
            
            # Load data from database
            df = self.query_data_from_db("silver_airline_quality_reviews", limit=None)
            df.rename(columns={'Type Of Traveller': 'traveller_type'}, inplace=True)
            df.columns = [c.lower().replace(' ', '_') for c in df.columns]
            print(df.columns)
            
            if df is None:
                print("Error: Failed to load data from database")
                return None
                
            if df.empty:
                print("Warning: Database returned empty dataset")
                # Cache the empty dataframe to avoid repeated database calls
                self.dashboard_cache[cache_key] = df
                return df
                
            print(f"Data loaded successfully: {len(df)} rows, {time.time() - start_time:.2f}s")
            
            # Preprocess data for faster operations
            preprocessing_start = time.time()
            
            # Convert review_date to datetime
            if 'review_date' in df.columns:
                try:
                    df['review_date'] = pd.to_datetime(df['review_date'], errors='coerce')
                    df['review_date_only'] = df['review_date'].dt.date
                except Exception as e:
                    print(f"Warning: Error converting review_date to datetime: {e}")
            
            # Convert overall_rating to numeric
            if 'overall_rating' in df.columns:
                try:
                    df['overall_rating'] = pd.to_numeric(df['overall_rating'], errors='coerce')
                except Exception as e:
                    print(f"Warning: Error converting overall_rating to numeric: {e}")
            
            print(f"Data preprocessing completed in {time.time() - preprocessing_start:.2f}s")
            
            # Extract and cache airline list
            if 'airline_name' in df.columns:
                try:
                    airlines = sorted(df['airline_name'].unique().tolist())
                    self.dashboard_cache['airlines_list'] = airlines
                    print(f"Found {len(airlines)} unique airlines")
                except Exception as e:
                    print(f"Warning: Error extracting airlines list: {e}")
            
            # Cache the processed data
            self.dashboard_cache[cache_key] = df
            
            print(f"Total data loading completed in {time.time() - start_time:.2f}s")
            return df
            
        except Exception as e:
            print(f"Error loading main data: {e}")
            return None
    
    def get_airlines(self):
        """Get list of airlines from database"""
        # Check if already in cache
        if 'airlines_list' in self.dashboard_cache:
            return self.dashboard_cache['airlines_list']
        
        # Load main data which will cache airlines list
        self._load_main_data()
        
        # Return from cache or empty list if not available
        return self.dashboard_cache.get('airlines_list', [])
    
    def _filter_by_airline(self, df, airline):
        """Filter dataframe by airline"""
        if airline != "All Airlines" and df is not None and 'airline_name' in df.columns:
            return df[df['airline_name'] == airline].copy()
        return df
    
    def execute_sql(self, sql_query, airline_filter=None):
        """Execute SQL-like query on the data"""
        # Load data
        df = self._load_main_data()
        if df is None or df.empty:
            return None
        
        # Apply airline filter if specified
        if airline_filter and airline_filter != "All Airlines":
            df = self._filter_by_airline(df, airline_filter)
        
        # Process SQL based on query pattern
        sql_lower = sql_query.lower()
        
        result = None
        
        # KPI metrics query
        if "count(1) as total_reviews" in sql_lower and "is_lost_luggage_flag" in sql_lower:
            result = self._calculate_kpi_metrics(df)
        
        # Rating distribution query
        elif "overall_rating" in sql_lower and "rating_count" in sql_lower:
            result = self._calculate_rating_distribution(df)
        
        # Traveler distribution query
        elif "traveller_type" in sql_lower and "traveller_count" in sql_lower:
            result = self._calculate_traveler_distribution(df)
        
        # Review trend query
        elif "review_day" in sql_lower and "review_count" in sql_lower:
            # Use one year instead of 30 days for trend
            result = self._calculate_review_trend(df)
        
        # Airline leaderboard query
        elif "airline_name" in sql_lower and "total_reviews" in sql_lower and "positive_reviews" in sql_lower:
            result = self._calculate_airline_leaderboard(df)
        
        return result
    
    def _calculate_kpi_metrics(self, df):
        """Calculate KPI metrics for dashboard"""
        if df is None or df.empty:
            return pd.DataFrame({
                'total_reviews': [0],
                'lost_reviews': [0],
                'yesterday_reviews': [0],
                'last_365_days_lost_reviews': [0]
            })
        
        # Get yesterday's date
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
        one_year_ago = (datetime.datetime.now() - datetime.timedelta(days=365)).date()
        
        # Process lost luggage flag
        if 'is_lost_luggage_flag' in df.columns:
            if df['is_lost_luggage_flag'].dtype == 'bool':
                lost_mask = df['is_lost_luggage_flag'] == True
            else:
                lost_mask = df['is_lost_luggage_flag'].isin(['1', 'true', 'True', 'TRUE', 'yes', 'Yes', 'YES', 'T', 't'])
        else:
            lost_mask = pd.Series([False] * len(df))
        
        # Ensure review_date_only column exists
        if 'review_date' in df.columns and 'review_date_only' not in df.columns:
            try:
                # Convert review_date to datetime if it's not already
                if df['review_date'].dtype != 'datetime64[ns]':
                    df['review_date'] = pd.to_datetime(df['review_date'], errors='coerce')
                # Extract date portion
                df['review_date_only'] = df['review_date'].dt.date
            except Exception as e:
                print(f"Error creating review_date_only column: {e}")
                # Create dummy column to prevent KeyError
                df['review_date_only'] = pd.NaT
        
        # Safely calculate metrics
        try:
            yesterday_count = 0
            last_365_days_lost_count = 0
            
            # Only calculate date-based metrics if the column exists and has valid data
            if 'review_date_only' in df.columns and not df['review_date_only'].isna().all():
                yesterday_mask = df['review_date_only'] == yesterday
                yesterday_count = yesterday_mask.sum()
                
                # Calculate last 365 days lost reviews
                last_365_days_mask = (df['review_date_only'] >= one_year_ago)
                last_365_days_lost_count = (last_365_days_mask & lost_mask).sum()
            
            result = pd.DataFrame({
                'total_reviews': [len(df)],
                'lost_reviews': [lost_mask.sum()],
                'yesterday_reviews': [yesterday_count],
                'last_365_days_lost_reviews': [last_365_days_lost_count]
            })
            return result
        except Exception as e:
            print(f"Error calculating KPI metrics: {e}")
            # Return fallback data to prevent dashboard crashes
            return pd.DataFrame({
                'total_reviews': [len(df)],
                'lost_reviews': [lost_mask.sum()],
                'yesterday_reviews': [0],
                'last_365_days_lost_reviews': [0]
            })
    
    def _calculate_rating_distribution(self, df):
        """Calculate rating distribution for dashboard"""
        if df is None or df.empty or 'overall_rating' not in df.columns:
            return pd.DataFrame(columns=['overall_rating', 'rating_count', 'avg_overall_rating'])
        
        # Filter valid ratings
        valid_df = df[df['overall_rating'].notna() & (df['overall_rating'] != 'NaN')]
        
        # Convert to numeric if needed
        if valid_df['overall_rating'].dtype == 'object':
            valid_df['overall_rating'] = pd.to_numeric(valid_df['overall_rating'], errors='coerce')
            valid_df = valid_df[valid_df['overall_rating'].notna()]
        
        if valid_df.empty:
            return pd.DataFrame(columns=['overall_rating', 'rating_count', 'avg_overall_rating'])
        
        # Group by rating
        result = valid_df.groupby('overall_rating').size().reset_index(name='rating_count')
        result['avg_overall_rating'] = valid_df['overall_rating'].mean()
        
        return result
    
    def _calculate_traveler_distribution(self, df):
        """Calculate traveler distribution for dashboard"""
        if df is None or df.empty or 'traveller_type' not in df.columns:
            return pd.DataFrame(columns=['traveller_type', 'traveller_count'])
        
        # Filter valid traveler types
        valid_df = df[df['traveller_type'].notna()]
        
        if valid_df.empty:
            return pd.DataFrame(columns=['traveller_type', 'traveller_count'])
        
        # Group by traveler type
        result = valid_df.groupby('traveller_type').size().reset_index(name='traveller_count')
        
        return result
    
    def _calculate_review_trend(self, df):
        """Calculate monthly review trend for dashboard"""
        # Create empty trend dataframe as a fallback
        empty_trend = self._create_empty_trend_dataframe()
        
        # Early return for empty dataframes
        if df is None or df.empty:
            return empty_trend
            
        try:
            # Ensure review_date is in datetime format
            if 'review_date' not in df.columns:
                print("Warning: review_date column not found in dataframe")
                return empty_trend
                
            # Make a copy to avoid modifying the original dataframe
            trend_df = df.copy()
            
            # Convert review_date to datetime if needed
            if trend_df['review_date'].dtype != 'datetime64[ns]':
                trend_df['review_date'] = pd.to_datetime(trend_df['review_date'], errors='coerce')
                
            # Drop rows with invalid dates
            trend_df = trend_df.dropna(subset=['review_date'])
            
            # If all dates are invalid, return empty dataframe
            if trend_df.empty:
                print("Warning: No valid dates found in dataframe")
                return empty_trend
            
            # Filter to last 12 months
            one_year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
            date_filtered = trend_df[trend_df['review_date'] >= one_year_ago]
            
            # Create monthly trend
            if not date_filtered.empty:
                # Extract year-month for grouping
                date_filtered['review_month'] = date_filtered['review_date'].dt.strftime('%Y-%m')
                
                # Ensure sentiment_label exists
                if 'sentiment_label' not in date_filtered.columns:
                    date_filtered['sentiment_label'] = 'unknown'
                
                # Group by month
                result = date_filtered.groupby('review_month').agg(
                    review_count=('review_month', 'count'),
                    positive_reviews=('sentiment_label', lambda x: (x == 'positive').sum()),
                    negative_reviews=('sentiment_label', lambda x: (x == 'negative').sum())
                ).reset_index()
            else:
                # No data in last year
                return empty_trend
            
            # Create complete month range for last 12 months
            today = datetime.datetime.now()
            month_range = [(today - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(12)]
            month_range.reverse()  # Oldest to newest
            
            # Create complete dataframe with all months
            complete_df = pd.DataFrame({'review_month': month_range})
            
            # Merge to ensure all months are included
            result = pd.merge(complete_df, result, on='review_month', how='left')
            
            # Fill NaN values with 0
            result.fillna(0, inplace=True)
            
            # Convert counts to integers
            result['review_count'] = result['review_count'].astype(int)
            result['positive_reviews'] = result['positive_reviews'].astype(int)
            result['negative_reviews'] = result['negative_reviews'].astype(int)
            
            # Sort by month
            result = result.sort_values('review_month')
            
            return result
            
        except Exception as e:
            print(f"Error calculating review trend: {e}")
            # Return empty trend on error
            return empty_trend
    
    def _create_empty_trend_dataframe(self):
        """Create empty trend dataframe with all months"""
        today = datetime.datetime.now()
        month_range = [(today - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(12)]
        month_range.reverse()  # Oldest to newest
        
        result = pd.DataFrame({'review_month': month_range})
        result['review_count'] = 0
        result['positive_reviews'] = 0
        result['negative_reviews'] = 0
        
        return result
    
    def _calculate_airline_leaderboard(self, df):
        """Calculate airline leaderboard for dashboard"""
        if df is None or df.empty:
            return pd.DataFrame(columns=['airline_name', 'total_reviews', 'positive_reviews', 'negative_reviews'])
        
        # Need to use the full dataset regardless of airline filter
        main_df = self._load_main_data()
        
        # Group by airline and calculate metrics
        result = main_df.groupby('airline_name').agg(
            total_reviews=('airline_name', 'count'),
            positive_reviews=('sentiment_label', lambda x: (x == 'positive').sum()),
            negative_reviews=('sentiment_label', lambda x: (x == 'negative').sum())
        ).reset_index()
        
        # Sort by total reviews and get top 15
        result = result.sort_values('total_reviews', ascending=False).head(15)
        
        return result
    
    def get_dashboard_metrics(self, metric_type, airline="All Airlines"):
        """Get specific dashboard metrics"""
        # Load data and filter by airline
        df = self._load_main_data()
        if df is None or df.empty:
            return None
        
        filtered_df = self._filter_by_airline(df, airline)
        
        # Calculate requested metrics
        if metric_type == 'kpi':
            return self._calculate_kpi_metrics(filtered_df)
        elif metric_type == 'rating':
            return self._calculate_rating_distribution(filtered_df)
        elif metric_type == 'traveler':
            return self._calculate_traveler_distribution(filtered_df)
        elif metric_type == 'trend':
            return self._calculate_review_trend(filtered_df)
        elif metric_type == 'leaderboard':
            return self._calculate_airline_leaderboard(filtered_df)
        
        return None
    
    def get_all_dashboard_data(self, airline="All Airlines"):
        """Get all dashboard data in a single call"""
        # Create cache key for this request
        cache_key = f"dashboard_data_{airline}"
        
        # Check if we need to reset cache
        self._should_reset_cache()
        
        # Return cached data if available
        if cache_key in self.dashboard_cache:
            return self.dashboard_cache[cache_key]
        
        # Load data and filter by airline
        df = self._load_main_data()
        if df is None or df.empty:
            return {
                'kpi': None,
                'rating_distribution': None,
                'traveler_distribution': None,
                'review_trend': None,
                'leaderboard': None
            }
        
        filtered_df = self._filter_by_airline(df, airline)
        
        # Calculate all metrics
        result = {
            'kpi': self._calculate_kpi_metrics(filtered_df),
            'rating_distribution': self._calculate_rating_distribution(filtered_df),
            'traveler_distribution': self._calculate_traveler_distribution(filtered_df),
            'review_trend': self._calculate_review_trend(filtered_df),
            'leaderboard': self._calculate_airline_leaderboard(df)  # Use full dataset for leaderboard
        }
        
        # Cache the result
        self.dashboard_cache[cache_key] = result
        
        return result
    
    def prepare_airline_data(self, airline):
        """Prepare data for a specific airline in advance"""
        # This will load and cache the data for this airline
        self.get_all_dashboard_data(airline)
        return {"status": "success", "message": f"Data prepared for {airline}"}


    