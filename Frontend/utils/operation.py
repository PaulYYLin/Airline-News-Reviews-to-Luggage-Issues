import pandas as pd
import requests
import time
from io import StringIO
from functools import lru_cache
import threading

class API_client:
    """
    Optimized API client with minimal frontend processing
    All heavy computation is performed on the backend
    """
    def __init__(self):
        # self.base_url = "http://localhost:8000"
        self.base_url = "http://34.203.42.231:8000"
        # Lightweight cache for frontend (shorter expiry to ensure fresh data)
        self.cache_timestamp = time.time()
        self.cache_expiry = 120  # 2 minutes 
        # Initialize dashboard data handler
        self.dashboard = DashboardDataHandler(self)
        # Track active background operations
        self.active_threads = []
        # Trigger backend to prepare data if needed
        self._ping_backend()
    
    def _ping_backend(self):
        """Ping backend to ensure it's running and has initialized data"""
        try:
            # Non-blocking request to the backend root to wake it up if dormant
            def ping_task():
                try:
                    requests.get(f"{self.base_url}/", timeout=2)
                except Exception:
                    # Ignore connection errors - the server might start up shortly
                    pass
            
            # Do this in a background thread to avoid blocking the UI
            thread = threading.Thread(target=ping_task, daemon=True)
            thread.start()
        except Exception:
            # Ignore any errors in the ping
            pass

    def _should_reset_cache(self):
        """Check if cache should be reset based on expiry time"""
        current_time = time.time()
        if current_time - self.cache_timestamp > self.cache_expiry:
            self.cache_timestamp = current_time
            # Clear cached methods
            self._cached_chat_with_chatbot.cache_clear()
            self._cached_get_reviews.cache_clear()
            self._cached_query_data_from_db.cache_clear()
            return True
        return False
    
    def query_data_from_db(self, table_name:str, limit:int):
        """Query data from database with caching"""
        self._should_reset_cache()
        return self._cached_query_data_from_db(table_name, limit)
    
    @lru_cache(maxsize=10)  # Reduced cache size to free up memory
    def _cached_query_data_from_db(self, table_name:str, limit:int):
        """LRU cached version of the database query"""
        try:
            response = requests.post(
                f"{self.base_url}/query_data_from_db", 
                params={"table_name": table_name, "limit": limit},
                timeout=10)
            
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                return None
                
            data = response.json()
            data = data.get('data', "{}")
            response_df = pd.read_json(StringIO(data), orient="records")
            
            # Minimal column standardization
            if 'Type Of Traveller' in response_df.columns:
                response_df.rename(columns={'Type Of Traveller': 'traveller_type'}, inplace=True)
            response_df.columns = [col.lower().replace(" ", "_") for col in response_df.columns]
            
            return response_df
        except Exception as e:
            print(f"Error querying database: {e}")
            return None
    
    def execute_sql(self, sql:str, airline_filter=None):
        """Execute SQL using backend endpoint"""
        try:
            params = {"sql": sql}
            if airline_filter:
                params["airline_filter"] = airline_filter
            
            response = requests.post(
                f"{self.base_url}/execute_sql", 
                json=params,
                timeout=10)
            
            if response.status_code != 200:
                print(f"Error executing SQL: {response.status_code}")
                return None
            
            data = response.json()
            if data.get('data'):
                return pd.read_json(StringIO(data['data']), orient="records")
            return None
        except Exception as e:
            print(f"Error executing SQL: {e}")
            return None
    
    def get_airlines(self):
        """Get list of airlines from backend"""
        try:
            response = requests.get(f"{self.base_url}/get_airlines", timeout=5)
            if response.status_code != 200:
                return []
            
            data = response.json()
            return data.get('airlines', [])
        except Exception as e:
            print(f"Error getting airlines: {e}")
            return []
        
    def get_kpi_metrics(self, airline:str):
        """Get KPI metrics from backend with airline filter"""
        return self.dashboard.get_metrics('kpi', airline)
        
    def get_rating_distribution(self, airline:str):
        """Get rating distribution from backend with airline filter"""
        return self.dashboard.get_metrics('rating', airline)
        
    def get_traveler_distribution(self, airline:str):
        """Get traveler distribution from backend with airline filter"""
        return self.dashboard.get_metrics('traveler', airline)
    
    @lru_cache(maxsize=50)
    def _cached_chat_with_chatbot(self, prompt:str):
        """Cached chatbot response"""
        try:
            response = requests.post(
                f"{self.base_url}/chat_with_chatbot",
                params={"prompt": prompt},
                timeout=30)  # Longer timeout for chatbot responses
            
            if response.status_code != 200:
                return f"Sorry, I encountered an error: {response.status_code}"
                
            data = response.json()
            return data.get('message', "Sorry, I couldn't process your request.")
        except Exception as e:
            return f"Error: {str(e)}"
    
    def chat_with_chatbot(self, prompt:str):
        """Chat with chatbot with caching"""
        self._should_reset_cache()
        return self._cached_chat_with_chatbot(prompt)
    
    @lru_cache(maxsize=5)
    def _cached_get_reviews(self, n:int):
        """Cached get reviews"""
        try:
            response = requests.get(
                f"{self.base_url}/get_last_n_reviews_for_ticker",
                params={"n": n},
                timeout=5)
            
            if response.status_code != 200:
                return []
                
            data = response.json()
            return data.get('items', [])
        except Exception as e:
            print(f"Error getting reviews: {e}")
            return []
    
    def get_last_n_reviews_for_ticker(self, n:int=10):
        """Get last n reviews with caching"""
        self._should_reset_cache()
        return self._cached_get_reviews(n)


class DashboardDataHandler:
    """
    Optimized dashboard data handler class
    Offloads all computation to backend
    """
    def __init__(self, api_client):
        self.api_client = api_client
        self.airlines_list = None
        # Add local cache for resilience
        self.local_cache = {}
    
    def get_metrics(self, metric_type:str, airline:str="All Airlines"):
        """
        Get specific dashboard metrics from backend
        Unified method for different chart data types
        """
        try:
            response = requests.get(
                f"{self.api_client.base_url}/get_dashboard_metrics",
                params={"metric_type": metric_type, "airline": airline},
                timeout=10)
            
            if response.status_code != 200:
                print(f"Error getting {metric_type} metrics: {response.status_code}")
                # Try to return cached data if available
                cache_key = f"{metric_type}_{airline}"
                if cache_key in self.local_cache:
                    return self.local_cache[cache_key]
                return None
                
            data = response.json()
            if data.get('data'):
                df = pd.read_json(StringIO(data['data']), orient="records")
                # Cache the result
                self.local_cache[f"{metric_type}_{airline}"] = df
                return df
            return None
        except Exception as e:
            print(f"Error getting {metric_type} metrics: {e}")
            # Try to return cached data if available
            cache_key = f"{metric_type}_{airline}"
            if cache_key in self.local_cache:
                return self.local_cache[cache_key]
            return None
    
    def get_airlines(self):
        """Get list of airlines from backend"""
        if self.airlines_list is not None:
            return self.airlines_list
        
        try:
            airlines = self.api_client.get_airlines()
            if airlines:
                self.airlines_list = airlines
                # Cache the airlines list locally
                self.local_cache["airlines"] = airlines
            else:
                # Fallback if empty list returned
                self.airlines_list = ["Default Airline"]
            return self.airlines_list
        except Exception as e:
            print(f"Error getting airlines: {e}")
            # Check if we have cached airlines
            if "airlines" in self.local_cache:
                return self.local_cache["airlines"]
            # Fallback to prevent UI crashes
            self.airlines_list = ["Default Airline"]
            return self.airlines_list
    
    def prepare_airline_data_async(self, airline):
        """
        Trigger the backend to prepare data for an airline
        This is done asynchronously to improve UI responsiveness
        """
        def _async_prepare():
            try:
                requests.post(
                    f"{self.api_client.base_url}/prepare_airline_data",
                    params={"airline": airline},
                    timeout=2)  # Short timeout - we don't need to wait for completion
            except Exception:
                # Silently ignore errors - this is just a prefetch
                pass
        
        # Create and track thread with minimal resources
        t = threading.Thread(target=_async_prepare, daemon=True)
        t.start()
        # No need to track the thread - it's lightweight and will terminate on its own
    
    def get_all_dashboard_data(self, airline="All Airlines"):
        """
        Get all dashboard data from backend in a single call
        """
        try:
            response = requests.get(
                f"{self.api_client.base_url}/get_all_dashboard_data",
                params={"airline": airline},
                timeout=15)  # Longer timeout for this comprehensive call
            
            if response.status_code != 200:
                print(f"Error getting dashboard data: {response.status_code}")
                # Try to use cached data if available
                if airline in self.local_cache:
                    return self.local_cache[airline]
                return self._get_empty_dashboard_data()
                
            data = response.json()
            
            # Convert JSON data to dataframes
            result = {}
            for key in ['kpi', 'rating_distribution', 'traveler_distribution', 'review_trend', 'leaderboard']:
                if key in data and data[key]:
                    result[key] = pd.read_json(StringIO(data[key]), orient="records")
                else:
                    result[key] = None
            
            # Cache the result for resilience
            self.local_cache[airline] = result
            
            # Prefetch data for other common selections in background
            if airline != "All Airlines":
                self.prepare_airline_data_async("All Airlines")
            elif self.airlines_list and len(self.airlines_list) > 0:
                self.prepare_airline_data_async(self.airlines_list[0])
                
            return result
        except Exception as e:
            print(f"Error getting all dashboard data: {e}")
            # Try to use cached data if available
            if airline in self.local_cache:
                return self.local_cache[airline]
            return self._get_empty_dashboard_data()
    
    def _get_empty_dashboard_data(self):
        """Return empty dashboard structure on error"""
        empty_df = pd.DataFrame()
        # Create empty data with the right structure to prevent UI errors
        kpi_df = pd.DataFrame({
            'total_reviews': [0],
            'lost_reviews': [0],
            'yesterday_reviews': [0],
            'yesterday_lost_reviews': [0]
        })
        
        # Create month-based empty data for trend
        today = pd.Timestamp.now()
        months = [(today - pd.DateOffset(months=i)).strftime('%Y-%m') for i in range(12)]
        months.reverse()
        trend_df = pd.DataFrame({
            'review_month': months,
            'review_count': [0] * 12,
            'positive_reviews': [0] * 12,
            'negative_reviews': [0] * 12
        })
        
        return {
            'kpi': kpi_df,
            'rating_distribution': empty_df,
            'traveler_distribution': empty_df,
            'review_trend': trend_df,
            'leaderboard': empty_df
        }


if __name__ == "__main__":
    api_client = API_client()
    print(api_client.query_data_from_db("silver_airline_quality_reviews", 2))