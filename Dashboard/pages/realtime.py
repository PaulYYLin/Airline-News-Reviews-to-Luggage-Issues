import streamlit as st
from styles import load_css
import pandas as pd
import os
from serpapi.google_search import GoogleSearch
from dotenv import load_dotenv

load_dotenv()
SERP_API_KEY = os.getenv("SERP_API_KEY")


def trigger_flight_search(origin:str, destination:str, departure_date:str, return_date:str, currency:str):

    params = {
    "engine": "google_flights",
    "departure_id": origin,
    "arrival_id": destination,
    "outbound_date": departure_date,
    "return_date": return_date,
    "currency": currency,
    "hl": "en",
    "api_key": SERP_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    return results




# Set page configuration
st.set_page_config(
    page_title="ALR-LP Realtime",
    page_icon="🛩️",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None,
)

# Load custom CSS
st.markdown(load_css(), unsafe_allow_html=True)

# Custom CSS for the ticker/marquee effect and styling
st.markdown("""
<style>
.ticker-container {
    background-color: rgba(50, 50, 50, 0.7);
    color: white;
    padding: 15px;
    border-radius: 5px;
    margin-bottom: 20px;
    overflow: hidden;
    position: relative;
    height: 60px;
    display: flex;
    align-items: center;
}

.ticker-text {
    white-space: nowrap;
    animation: ticker 30s linear infinite;
    font-size: 1.1rem;
    position: absolute;
}

@keyframes ticker {
    0% { transform: translateX(100%); }
    100% { transform: translateX(-100%); }
}

/* Custom styling for Streamlit elements */
div.element-container div.stButton > button {
    background-color: rgba(50, 50, 50, 0.5);
    color: white;
    border-radius: 50px;
    padding: 10px 25px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    font-weight: 500;
    transition: all 0.3s;
    width: 100%;
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

div.element-container div.stButton > button:hover {
    background-color: rgba(80, 80, 80, 0.7);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.filter-container {
    background-color: rgba(50, 50, 50, 0.3);
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 20px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Input area styling */
.stTextInput > div > div > input {
    background-color: rgba(30, 30, 30, 0.7);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 5px;
}

.stSelectbox > div > div > div {
    background-color: rgba(30, 30, 30, 0.7) !important;
    color: white !important;
}

/* Logo and header styling */
.header-container {
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state for reviews ticker
if 'reviews' not in st.session_state:
    st.session_state.reviews = ["I had a great time at WestJet lounge", 
                              "The flight attendants were very helpful", 
                              "Terrible service and delayed flight",
                              "My luggage was damaged during the flight",
                              "Security at YVR was extremely efficient"]

# Header and ticker at the top
st.markdown('<div class="header-container"><div class="logo-text">REALTIME PILOT</div></div>', unsafe_allow_html=True)

# Create a ticker display with all the reviews
all_reviews = " • ".join(st.session_state.reviews)
st.markdown(f"""
<div class="ticker-container">
    <div class="ticker-text">
        {all_reviews}
    </div>
</div>
""", unsafe_allow_html=True)

# Create full dataset (including both airlines and airports)
all_data = {
    "Rank": list(range(1, 13)),
    "Entity": [
        "Air Canada", "WestJet", "United Airlines", "Delta", 
        "American Airlines", "JetBlue", "British Airways", "Lufthansa",
        "YVR Vancouver", "YYZ Toronto", "LAX Los Angeles", "JFK New York"
    ],
    "Type": [
        "Airline", "Airline", "Airline", "Airline", 
        "Airline", "Airline", "Airline", "Airline",
        "Airport", "Airport", "Airport", "Airport"
    ],
    "Sentiment Score": [
        85, 78, 72, 68, 63, 59, 54, 48, 82, 75, 70, 65
    ],
}

# Add rank change with visual indicators
rank_changes = [
    "+2", "-1", "+3", "0", "-2", "+1", "-3", "+2", 
    "+1", "-2", "0", "+3"
]
rank_change_visuals = []

for change in rank_changes:
    if change.startswith("+"):
        rank_change_visuals.append(f"↑ {change[1:]}")
    elif change.startswith("-"):
        rank_change_visuals.append(f"↓ {change[1:]}")
    else:
        rank_change_visuals.append(f"→ {change}")

all_data["Rank Change"] = rank_change_visuals
all_data["Issues"] = [
    "Luggage Delayed", "None", "Luggage Lost", "Luggage Damaged", 
    "Luggage Delayed", "None", "Luggage Lost", "Luggage Damaged",
    "Security Delays", "Check-in Issues", "None", "Security Delays"
]

# Convert to DataFrame for easier filtering
full_df = pd.DataFrame(all_data)

# Filter section
filter_col1, filter_col2 = st.columns([1, 1])

with filter_col1:
    entity_type = st.selectbox("Entity Type", ["All", "Airline", "Airport"], key="entity_type")

with filter_col2:
    issue_type = st.selectbox("Issue Type", ["All", "Luggage Lost", "Luggage Damaged", "Luggage Delayed", "Security Delays", "Check-in Issues"], key="issue_type")
st.markdown('</div>', unsafe_allow_html=True)

# Apply filters to dataframe
filtered_df = full_df.copy()

# Filter by entity type
if entity_type != "All":
    filtered_df = filtered_df[filtered_df["Type"] == entity_type]

# Filter by issue type
if issue_type != "All":
    filtered_df = filtered_df[filtered_df["Issues"] == issue_type]


# Reindex ranks after filtering
filtered_df = filtered_df.reset_index(drop=True)
filtered_df["Rank"] = filtered_df.index + 1

# Display the table header and flight search header in the same row
header_left, header_right = st.columns([1, 1])
with header_left:
    st.markdown("<h2>Entity Rankings by Sentiment</h2>", unsafe_allow_html=True)
with header_right:
    st.markdown("<h2>Flight Search</h2>", unsafe_allow_html=True)

# Create two columns layout - left for table, right for Google Flight API
left_col, right_col = st.columns([1, 1])

# Display filtered data in the left column
with left_col:
    if filtered_df.empty:
        st.warning("No results match your filter criteria. Please adjust your filters.")
    else:
            # Remove the Type column before displaying
            display_df = filtered_df.drop(columns=["Type"])
            
        # Use the native st.dataframe with styling
    st.dataframe(
            display_df,
        column_config={
            "Rank": st.column_config.NumberColumn(
                "Rank",
                help="Current ranking position",
                format="%d",
                width="small",
            ),
            "Entity": st.column_config.TextColumn(
                "Entity",
                help="Airline or airport name",
                width="medium",
            ),
            "Sentiment Score": st.column_config.ProgressColumn(
                "Sentiment Score",
                help="Sentiment score based on reviews (0-100)",
                format="%d",
                min_value=0,
                max_value=100,
                width="medium",
            ),
            "Rank Change": st.column_config.TextColumn(
                "Rank Change",
                help="Change in ranking position",
                width="small",
            ),
            "Issues": st.column_config.TextColumn(
                "Issues",
                help="Reported luggage issues",
                width="medium",
            ),
        },
        hide_index=True,
        use_container_width=True,
            height=500,  # Increase height to match the form + results
        )

# Add Google Flight API interface in the right column
with right_col:
    # Add a container with matching height for the flight search form
    with st.container():
        # Add flight search form
        with st.form("flight_search_form"):
            # Origin and destination
            origin = st.text_input("From (Airport Code)", placeholder="YVR", value="YVR")
            destination = st.text_input("To (Airport Code)", placeholder="YYZ", value="YYZ")
            
            # Date selection
            col1, col2 = st.columns(2)
            with col1:
                departure_date = st.date_input("Departure Date")
            with col2:
                return_date = st.date_input("Return Date")
            
            # Currency selection
            currency = st.selectbox("Currency", ["CAD", "USD", "EUR", "GBP"], index=0)
            
            # Submit button
            search_submitted = st.form_submit_button("Search Flights")
        
        # Display flight search results
        if search_submitted:
            # Show loading spinner
            with st.spinner("Searching for flights..."):
                try:
                    # 將日期轉換為字串格式
                    dep_date_str = departure_date.strftime("%Y-%m-%d")
                    ret_date_str = return_date.strftime("%Y-%m-%d")
                    
                    flight_data = trigger_flight_search(origin, destination, dep_date_str, ret_date_str, currency)
                    
                    if flight_data:
                        # Display summary header
                        st.markdown(f"""
                        <div style="background-color: rgba(30, 30, 30, 0.7); padding: 15px; border-radius: 10px; 
                                    border: 1px solid rgba(255, 255, 255, 0.1);">
                            <h3>Flight Search Results</h3>
                            <p>Route: {origin} → {destination}</p>
                            <p>Dates: {departure_date.strftime("%b %d, %Y")} - {return_date.strftime("%b %d, %Y")}</p>
                        """, unsafe_allow_html=True)
                        
                        # Check if we have best flights data
                        if "best_flights" in flight_data and len(flight_data["best_flights"]) > 0:
                            st.markdown("""
                            <h4 style="margin-top: 15px;">Best Flight Options:</h4>
                            """, unsafe_allow_html=True)
                            
                            # Create a container for flight options
                            for i, flight_option in enumerate(flight_data["best_flights"][:3]):  # Display top 3 options
                                # 基本航班信息
                                price = f"{currency} {flight_option.get('price', 'N/A')}"
                                flight_type = flight_option.get('type', 'One-way')
                                
                                # 取得航班詳細信息
                                flights = flight_option.get('flights', [])
                                layovers = flight_option.get('layovers', [])
                                total_duration = flight_option.get('total_duration', 0)
                                
                                # 計算總飛行時間（小時和分鐘）
                                hours = total_duration // 60
                                minutes = total_duration % 60
                                duration_str = f"{hours}h {minutes}m"
                                
                                # 航空公司資訊
                                airlines = list(set([f["airline"] for f in flights if "airline" in f]))
                                airline_str = ", ".join(airlines)
                                
                                # 停靠站數量
                                stops = len(layovers)
                                stops_str = "Direct" if stops == 0 else f"{stops} stop{'s' if stops > 1 else ''}"
                                
                                # 航班路徑摘要
                                if flights and len(flights) > 0:
                                    first_flight = flights[0]
                                    last_flight = flights[-1]
                                    route_str = f"{first_flight['departure_airport']['id']} → "
                                    
                                    # 添加中間停靠站
                                    if stops > 0:
                                        route_str += " → ".join([layover['id'] for layover in layovers]) + " → "
                                    
                                    route_str += f"{last_flight['arrival_airport']['id']}"
                                else:
                                    route_str = f"{origin} → {destination}"
                                
                                # 顯示航班信息卡片
                                st.markdown(f"""
                                <div style="background-color: rgba(50, 50, 50, 0.7); padding: 15px; 
                                            margin-top: 15px; border-radius: 5px; border: 1px solid rgba(255, 255, 255, 0.05);">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                        <div style="font-weight: bold; font-size: 16px;">{airline_str}</div>
                                        <div style="font-weight: bold; color: #4CAF50; font-size: 18px;">{price}</div>
                                    </div>
                                    <div style="margin-bottom: 8px;">{route_str}</div>
                                    <div style="display: flex; justify-content: space-between; margin-top: 8px;">
                                        <div>{stops_str}</div>
                                        <div>{duration_str}</div>
                                        <div>{flight_type}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # 顯示詳細航班信息（摺疊顯示）
                                if len(flights) > 0:
                                    st.markdown("""
                                    <div style="margin-top: 10px; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 10px;">
                                        <details>
                                            <summary style="cursor: pointer; color: #64B5F6;">Flight Details</summary>
                                            <div style="margin-top: 10px;">
                                    """, unsafe_allow_html=True)
                                    
                                    for j, flight in enumerate(flights):
                                        dep_airport = flight.get('departure_airport', {})
                                        arr_airport = flight.get('arrival_airport', {})
                                        flight_airline = flight.get('airline', 'Unknown')
                                        flight_number = flight.get('flight_number', 'N/A')
                                        flight_duration = flight.get('duration', 0)
                                        flight_duration_str = f"{flight_duration // 60}h {flight_duration % 60}m"
                                        
                                        st.markdown(f"""
                                        <div style="margin-bottom: 8px; padding: 8px; background-color: rgba(40, 40, 40, 0.5); border-radius: 4px;">
                                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                                <div>{dep_airport.get('id', 'N/A')} {dep_airport.get('time', 'N/A')}</div>
                                                <div>→</div>
                                                <div>{arr_airport.get('id', 'N/A')} {arr_airport.get('time', 'N/A')}</div>
                                            </div>
                                            <div style="font-size: 0.9em; color: #BBB;">
                                                {flight_airline} {flight_number} · {flight_duration_str}
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        # 顯示停留信息（如果有下一個航班）
                                        if j < len(flights) - 1 and j < len(layovers):
                                            layover = layovers[j]
                                            layover_duration = layover.get('duration', 0)
                                            layover_hours = layover_duration // 60
                                            layover_minutes = layover_duration % 60
                                            layover_str = f"{layover_hours}h {layover_minutes}m"
                                            
                                            st.markdown(f"""
                                            <div style="margin: 5px 0 10px 20px; color: #FFB74D; font-size: 0.9em;">
                                                Layover: {layover.get('name', 'N/A')} ({layover_str})
                                                {' <span style="color: #FF8A65;">(Overnight)</span>' if layover.get('overnight', False) else ''}
                                            </div>
                                            """, unsafe_allow_html=True)
                                    
                                    st.markdown("""
                                            </div>
                                        </details>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                st.markdown("</div>", unsafe_allow_html=True)
                            
                            # "查看更多航班" 按鈕（如果有更多選項）
                            if len(flight_data["best_flights"]) > 3:
                                st.markdown("""
                                <div style="text-align: center; margin-top: 15px;">
                                    <button style="background-color: rgba(70, 70, 70, 0.7); border: 1px solid rgba(255, 255, 255, 0.2); 
                                            color: white; padding: 8px 15px; border-radius: 20px; cursor: pointer;">
                                        View More Options
                                    </button>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # 如果沒有找到航班
                        elif "error" in flight_data:
                            st.error(f"Error: {flight_data['error']}")
                        else:
                            st.warning("No flights found for this route and dates. Please try different search criteria.")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.error("Error: Unable to fetch flight data")
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    
                    # Fallback to show sample data
                    st.markdown(f"""
                    <div style="background-color: rgba(30, 30, 30, 0.7); padding: 15px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.1);">
                        <h3>Sample Flight Results</h3>
                        <p>Route: {origin} → {destination}</p>
                        <p>Departure: {departure_date.strftime("%b %d, %Y")}</p>
                        <p>Return: {return_date.strftime("%b %d, %Y")}</p>
                        
                        <div style="background-color: rgba(50, 50, 50, 0.7); padding: 10px; margin-top: 15px; border-radius: 5px;">
                            <p><strong>Sample Flight Options:</strong></p>
                            <ul style="padding-left: 20px;">
                                <li>Air Canada - {currency} 450 - 5h 15m (Direct)</li>
                                <li>WestJet - {currency} 380 - 5h 30m (Direct)</li>
                                <li>United - {currency} 420 - 7h 45m (1 Stop)</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Enter your flight details and click 'Search Flights' to see available options.")

# Add navigation back to home using native Streamlit button
st.markdown("<div style='height: 30px'></div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("BACK TO HOME", use_container_width=True):
        st.switch_page("pages/home.py")
