import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="ESP32 Sensor Dashboard", page_icon="🌡️", layout="wide")

st.title("🌡️ ESP32 Sensor Data Dashboard")
st.markdown("Real-time monitoring of temperature and humidity from the SQLite database.")

# Connect to database
DB_PATH = os.path.join(os.path.dirname(__file__), "backend", "sensor_data.db")

def load_data():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT timestamp, temperature, humidity FROM sensor_data ORDER BY timestamp DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        return df
        
    # Convert timestamp to datetime if not already
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # Sort chronologically for charting
    df = df.sort_values('timestamp')
    return df

try:
    df = load_data()
    
    if not df.empty:
        # Create a layout with metrics at the top
        col1, col2, col3 = st.columns(3)
        latest = df.iloc[-1]
        
        col1.metric("Latest Temperature", f"{latest['temperature']:.1f} °C")
        col2.metric("Latest Humidity", f"{latest['humidity']:.1f} %")
        col3.metric("Total Readings", len(df))
        
        st.divider()
        
        # Charts
        st.subheader("Data Trends")
        
        tab1, tab2, tab3 = st.tabs(["Combined Chart", "Temperature", "Humidity"])
        
        with tab1:
            st.line_chart(df.set_index("timestamp")[["temperature", "humidity"]], use_container_width=True)
            
        with tab2:
            st.line_chart(df.set_index("timestamp")["temperature"], color="#ff4b4b", use_container_width=True)
            
        with tab3:
            st.line_chart(df.set_index("timestamp")["humidity"], color="#0068c9", use_container_width=True)
            
        st.divider()
        
        # Raw Data
        st.subheader("Raw Data")
        st.dataframe(df.sort_values('timestamp', ascending=False), use_container_width=True)
        
    else:
        st.info("No sensor data found in the database. Please insert some data first.")
        
except Exception as e:
    st.error(f"Error loading database from {DB_PATH}: {e}")
