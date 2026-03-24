import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import os
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# -----------------
# Page Settings
# -----------------
st.set_page_config(page_title="ESP32 Sensor Dashboard", page_icon="🌡️", layout="wide")

# Custom CSS for better UI aesthetics
st.markdown("""
<style>
    .metric-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        text-align: center;
    }
    .stMetric {
        background-color: #1a1a2e;
        padding: 20px !important;
        border-radius: 15px !important;
        border-left: 5px solid #00d2ff !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
    }
    .stMetric label {
        color: #b0c4de !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------
# Sidebar Controls
# -----------------
st.sidebar.title("⚙️ Dashboard Settings")
st.sidebar.markdown("Configure the data source and view settings below.")

data_source = st.sidebar.radio(
    "Data Source",
    options=["Live Database (Local)", "Random Mock Data (Demo)"],
    index=0,
    help="Choose 'Live Database' when connected to the local SQLite DB, or 'Random Mock Data' for public web deployment demos."
)

st.sidebar.divider()
records_limit = st.sidebar.slider("Number of Records to Display", min_value=10, max_value=500, value=100, step=10)

if data_source == "Live Database (Local)":
    if st.sidebar.button("🔄 Refresh Data"):
        pass # Button click automatically triggers a script rerun
        
    # Automatically triggers a frontend rerun every 5000 milliseconds (5 seconds)
    st_autorefresh(interval=5000, limit=None, key="live_data_updater")
else:
    if st.sidebar.button("🎲 Clear & Regenerate Mock Data"):
        st.session_state.mock_df = None # Clears the rolling history
        
    # Automatically triggers a frontend rerun every 1000 milliseconds (1 second)
    st_autorefresh(interval=1000, limit=None, key="mock_data_updater")

# -----------------
# Data Loading Logic
# -----------------
def load_db_data(limit):
    DB_PATH = os.path.join(os.path.dirname(__file__), "backend", "sensor_data.db")
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
        
    try:
        conn = sqlite3.connect(DB_PATH)
        query = f"SELECT timestamp, temperature, humidity FROM sensor_data ORDER BY timestamp DESC LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
        return df
    except Exception:
        return pd.DataFrame()

def update_mock_data(limit):
    # If the user just switched or clicked Clear, initialize a base dataset
    if "mock_df" not in st.session_state or st.session_state.mock_df is None:
        np.random.seed(int(datetime.now().timestamp()))
        end_time = datetime.now()
        start_time = end_time - timedelta(seconds=limit)
        timestamps = pd.date_range(start=start_time, end=end_time, periods=limit)
        temps = np.cumsum(np.random.normal(0, 0.2, limit)) + 26.0
        hums = np.cumsum(np.random.normal(0, 0.5, limit)) + 55.0
        
        temps = np.clip(temps, 15.0, 40.0)
        hums = np.clip(hums, 30.0, 90.0)
        
        df = pd.DataFrame({'timestamp': timestamps, 'temperature': temps, 'humidity': hums})
        st.session_state.mock_df = df
        return df

    # We already have data, let's append exactly 1 new random point for the sliding window effect
    df = st.session_state.mock_df
    now = datetime.now()
    
    last_temp = df['temperature'].iloc[-1]
    last_hum = df['humidity'].iloc[-1]
    
    new_temp = np.clip(last_temp + np.random.normal(0, 0.2), 15.0, 40.0)
    new_hum = np.clip(last_hum + np.random.normal(0, 0.5), 30.0, 90.0)
    
    new_row = pd.DataFrame({'timestamp': [now], 'temperature': [new_temp], 'humidity': [new_hum]})
    
    # Append the row
    df = pd.concat([df, new_row], ignore_index=True)
    
    # Prune exactly to limit so it doesn't leak memory (Sliding Window)
    if len(df) > limit:
        df = df.iloc[-limit:]
        
    st.session_state.mock_df = df
    return df

# Fetch Data based on choice
if data_source == "Live Database (Local)":
    df = load_db_data(records_limit)
else:
    df = update_mock_data(records_limit)

# -----------------
# Main UI Rendering
# -----------------
st.title("🌡️ ESP32 Real-Time Environment Dashboard")
st.markdown("Monitor your space precisely. **Use buttons on the left to manually refresh.**")

if df.empty:
    if data_source == "Live Database (Local)":
        st.error("🚨 **Error: Local Database Not Found or Empty!**")
        st.info("We could not read any sensor data from `backend/sensor_data.db`. This usually means the ESP32 hasn't sent any data yet, or the backend server hasn't created the database. \n\n👉 **Tip: Switch Data Source to 'Random Mock Data (Demo)' in the left sidebar to preview the dashboard features!**")
    else:
        st.warning("⚠️ No data could be generated.")
else:
    # -----------------
    # Top Metrics Board
    # -----------------
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Temperature", f"{latest['temperature']:.1f} °C", 
                  delta=f"{(latest['temperature'] - prev['temperature']):.1f} °C")
    with col2:
        st.metric("Humidity", f"{latest['humidity']:.1f} %", 
                  delta=f"{(latest['humidity'] - prev['humidity']):.1f} %")
    with col3:
        st.metric("Total Records", f"{len(df)}", delta="Active")
    with col4:
        st.metric("Data Source", data_source.split(" ")[0], delta="Online", delta_color="normal")
        
    st.divider()

    # -----------------
    # Interactive Plotly Charts
    # -----------------
    st.subheader("📈 Detailed Temporal Trends")
    st.markdown("Hover over the lines for exact timestamps. Drag to zoom in on specific intervals.")
    
    # Main Combined Chart
    fig = px.line(df, x="timestamp", y=["temperature", "humidity"], 
                  title="Temperature & Humidity Co-relation",
                  labels={"value": "Sensor Value", "timestamp": "Timestamp", "variable": "Metric"},
                  template="plotly_dark", 
                  color_discrete_sequence=["#ff4b4b", "#00d2ff"])
    
    fig.update_xaxes(
        tickformat="%Y-%m-%d %H:%M:%S",
        title_text="Exact Time",
        showgrid=True, gridwidth=1, gridcolor='#333333'
    )
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#333333')
    fig.update_layout(hovermode="x unified", legend_title_text='Sensors')
    
    st.plotly_chart(fig)
    
    st.divider()
    
    # Side-by-Side Specific Views
    st.subheader("📉 Micro View")
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        fig_temp = px.area(df, x="timestamp", y="temperature", title="Temperature Fluidity",
                         color_discrete_sequence=["#ff4b4b"], template="plotly_dark")
        fig_temp.update_xaxes(tickformat="%H:%M:%S", showgrid=True)
        st.plotly_chart(fig_temp)
        
    with col_chart2:
        fig_hum = px.area(df, x="timestamp", y="humidity", title="Humidity Fluidity",
                        color_discrete_sequence=["#00d2ff"], template="plotly_dark")
        fig_hum.update_xaxes(tickformat="%H:%M:%S", showgrid=True)
        st.plotly_chart(fig_hum)

    with st.expander("👀 View Raw Data Table"):
        st.dataframe(df.sort_values('timestamp', ascending=False))
