from fastapi import FastAPI, Query, Body
from exe import Executor
from typing import Optional, Dict, Any
import uvicorn
from pydantic import BaseModel
import pandas as pd
from io import StringIO
import time


# Initialize backend executor once at startup
# This will trigger data preloading in a background thread
backend_executor = Executor.get_instance()

# Track backend initialization status
backend_status = {
    "startup_time": time.time(),
    "initialized": False,
    "data_loaded": False,
    "airlines_loaded": False,
    "errors": []
}

# API endpoints
app = FastAPI(title="Reddit Data Processing API")

@app.on_event("startup")
async def startup_event():
    """Initialize data on server startup"""
    # This will initialize the executor and start preloading essential data
    global backend_executor, backend_status
    print("FastAPI server starting - initializing backend data...")
    
    # Start background initialization
    def init_backend():
        global backend_status
        try:
            # Load main data
            main_data = backend_executor._load_main_data()
            if main_data is not None:
                backend_status["data_loaded"] = True
                
                # Get airlines
                airlines = backend_executor.get_airlines()
                if airlines and len(airlines) > 0:
                    backend_status["airlines_loaded"] = True
            
            # Mark as initialized regardless of data load status
            backend_status["initialized"] = True
        except Exception as e:
            backend_status["errors"].append(str(e))
            print(f"Error during backend initialization: {e}")
    
    # Run initialization in background to avoid blocking server startup
    import threading
    init_thread = threading.Thread(target=init_backend)
    init_thread.daemon = True
    init_thread.start()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Reddit Data Processing API"}

@app.get("/health")
def health_check():
    """Health check endpoint that returns backend initialization status"""
    global backend_status
    
    # Calculate uptime
    uptime = time.time() - backend_status["startup_time"]
    
    # Check if data is available
    has_airlines = len(backend_executor.get_airlines()) > 0 if backend_status["initialized"] else False
    if has_airlines:
        backend_status["airlines_loaded"] = True
    
    # Check data in cache
    has_data = "main_data" in backend_executor.dashboard_cache
    if has_data:
        backend_status["data_loaded"] = True
    
    return {
        "status": "ready" if backend_status["initialized"] else "initializing",
        "uptime_seconds": uptime,
        "initialized": backend_status["initialized"],
        "data_loaded": backend_status["data_loaded"],
        "airlines_loaded": backend_status["airlines_loaded"],
        "errors": backend_status["errors"],
        "airlines_count": len(backend_executor.get_airlines()) if backend_status["airlines_loaded"] else 0,
        "cache_entries": len(backend_executor.dashboard_cache)
    }

@app.post("/trigger_realtime_reddit_spider")
def trigger_realtime_reddit_spider(
    subreddit_name: str = Query("all", enum=["all", "travel","flight","flying","travelhacks","airtravel"]),
    time_filter: str = Query("day", enum=["day", "week", "month", "year", "all"]),
    limit: int = Query(10, ge=1, le=100),
    sort: str = Query("new", enum=["hot", "new", "top", "relevance"])
):
    # Use the global executor instance
    global backend_executor
    num_posts = backend_executor.trigger_realtime_reddit_spider(time_filter, limit, subreddit_name, sort)
    return {"message": f"Collected {num_posts} posts {subreddit_name} | {time_filter} | {limit} | {sort}"}

@app.post("/trigger_airquality_spider")
def trigger_airquality_spider(days_before_today: int = Query(3, ge=1, le=30)):
    # Use the global executor instance
    global backend_executor
    reviews_df = backend_executor.trigger_airquality_spider(days_before_today)
    return {"message": f"Collected {len(reviews_df)} reviews"}


# For Frontend =======================================================================

@app.post("/query_data_from_db")
def query_data_from_db(table_name: str = Query(..., description="The name of the table to query"), 
                       limit: int =  Query(None, description="The number of records to return")):
    # Use the global executor instance
    global backend_executor
    df = backend_executor.query_data_from_db(table_name, limit)
    df = df.to_json(orient="records")
    
    return {"data": df}


@app.post("/chat_with_chatbot")
def chat_with_chatbot(prompt: str = Query(...)):
    # Use the global executor instance
    global backend_executor
    response = backend_executor.chat_with_chatbot(prompt)
    return {"message": response}


@app.get("/get_last_n_reviews_for_ticker")
def get_last_n_reviews_for_ticker(n: int = Query(10, ge=1, le=100)):
    # Use the global executor instance
    global backend_executor
    reviews = backend_executor.get_last_n_reviews_for_ticker(n)
    return {"items": reviews}

# Dashboard data endpoints =======================================================================

@app.get("/get_airlines")
def get_airlines():
    """Get list of airlines for the dashboard"""
    # Use the global executor instance
    global backend_executor
    airlines = backend_executor.get_airlines()
    return {"airlines": airlines}

@app.post("/execute_sql")
def execute_sql(query_params: Dict[str, Any] = Body(...)):
    """Execute SQL-like query on the data"""
    # Use the global executor instance
    global backend_executor
    
    sql = query_params.get("sql", "")
    airline_filter = query_params.get("airline_filter")
    
    result_df = backend_executor.execute_sql(sql, airline_filter)
    
    if result_df is not None:
        return {"data": result_df.to_json(orient="records")}
    
    return {"data": None}

@app.get("/get_dashboard_metrics")
def get_dashboard_metrics(
    metric_type: str = Query(..., description="Type of metrics to get (kpi, rating, traveler, trend, leaderboard)"),
    airline: str = Query("All Airlines", description="Airline to filter by")
):
    """Get specific dashboard metrics"""
    # Use the global executor instance
    global backend_executor
    
    result_df = backend_executor.get_dashboard_metrics(metric_type, airline)
    
    if result_df is not None:
        return {"data": result_df.to_json(orient="records")}
    
    return {"data": None}

@app.get("/get_all_dashboard_data")
def get_all_dashboard_data(
    airline: str = Query("All Airlines", description="Airline to filter by")
):
    """Get all dashboard data in a single call"""
    try:
        # Use the global executor instance
        global backend_executor
        
        result = backend_executor.get_all_dashboard_data(airline)
        
        # Ensure all expected keys exist
        expected_keys = ['kpi', 'rating_distribution', 'traveler_distribution', 'review_trend', 'leaderboard']
        for key in expected_keys:
            if key not in result:
                result[key] = None
        
        response = {}
        for key, df in result.items():
            if df is not None:
                try:
                    response[key] = df.to_json(orient="records")
                except Exception as e:
                    print(f"Error converting {key} to JSON: {e}")
                    response[key] = None
            else:
                response[key] = None
        
        return response
    except Exception as e:
        import traceback
        print(f"Error in get_all_dashboard_data: {e}")
        print(traceback.format_exc())  # Add this line for more detailed error info
        # Return empty but valid structure on error
        return {
            'kpi': None,
            'rating_distribution': None,
            'traveler_distribution': None, 
            'review_trend': None,
            'leaderboard': None
        }

@app.post("/prepare_airline_data")
def prepare_airline_data(
    airline: str = Query(..., description="Airline to prepare data for")
):
    """Prepare data for a specific airline in advance"""
    # Use the global executor instance
    global backend_executor
    result = backend_executor.prepare_airline_data(airline)
    return result


if __name__ == "__main__":
    import requests
    import threading
    import time
    
    # Start the server in a separate thread
    def run_server():
        uvicorn.run(app, host="0.0.0.0", port=8000)
    
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Give the server time to start
    time.sleep(2)
    
    # Define base URL
    base_url = "http://localhost:8000"
    
    # # Test the endpoint
    # try:
    #     print("Testing /query_data_from_db endpoint...")
    #     response = requests.post(
    #         f"{base_url}/query_data_from_db",
    #         params={
    #             "table_name": "silver_airline_quality_reviews",
    #             "limit": 5,
    #         }
    #     )
    #     print(f"Status Code: {response.status_code}")
    #     print(f"Response: {response.json()}")
    # except Exception as e:
    #     print(f"Error testing endpoint: {str(e)}")
    # Keep the main thread running
    server_thread.join()
