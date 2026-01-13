from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from datetime import datetime
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "data/hives.db"
os.makedirs("data", exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS hives
                 (hive_id INTEGER PRIMARY KEY,
                  weight_kg REAL,
                  level INTEGER,
                  extracting BOOLEAN DEFAULT 0,
                  last_update TEXT)''')
    conn.commit()
    conn.close()

init_db()

class HiveData(BaseModel):
    hive: int
    weight_kg: float
    extracting: bool = False

@app.post("/beehive")
async def receive_data(data: HiveData):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now().isoformat()
    level = round((data.weight_kg / 12) * 100)
    level = max(0, min(100, level))
    c.execute('''INSERT OR REPLACE INTO hives 
                 (hive_id, weight_kg, level, extracting, last_update)
                 VALUES (?, ?, ?, ?, ?)''',
              (data.hive, data.weight_kg, level, data.extracting, now))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.get("/beehive/{hive_id}/harvest-status")
async def harvest_status(hive_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT extracting FROM hives WHERE hive_id = ?", (hive_id,))
    result = c.fetchone()
    conn.close()
    return "true" if result and result[0] else "false"

@app.post("/beehive/{hive_id}/harvest-complete")
async def harvest_complete(hive_id: int):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE hives SET extracting = 0 WHERE hive_id = ?", (hive_id,))
    conn.commit()
    conn.close()
    return {"status": "complete"}
