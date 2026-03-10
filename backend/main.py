import sqlite3
import os
from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_DIR = os.path.dirname(__file__)
DB_FILE = os.path.join(DB_DIR, "sensor_data.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup
    init_db()
    yield
    # Teardown (if needed)

app = FastAPI(title="ESP32 Sensor Backend", lifespan=lifespan)

class SensorData(BaseModel):
    temperature: float
    humidity: float

class SensorDataResponse(SensorData):
    id: int
    timestamp: datetime

@app.post("/sensor-data", status_code=201)
def add_sensor_data(data: SensorData):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sensor_data (temperature, humidity) VALUES (?, ?)",
            (data.temperature, data.humidity)
        )
        conn.commit()
        conn.close()
        return {"message": "Data saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sensor-data", response_model=List[SensorDataResponse])
def get_sensor_data(limit: int = 100):
    try:
        conn = sqlite3.connect(DB_FILE)
        # Using row_factory to return dictionaries
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, temperature, humidity, timestamp FROM sensor_data ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
