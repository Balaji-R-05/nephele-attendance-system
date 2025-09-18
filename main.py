from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from datetime import date
from contextlib import asynccontextmanager

DB_NAME = "attendance.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT,
        name TEXT,
        reg_no TEXT,
        dept TEXT,
        extra_info TEXT,
        date TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(roll_no, date)
    )
    """)
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up... Initializing DB")
    init_db()
    yield
    print("🛑 Shutting down... Cleanup here if needed")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QRData(BaseModel):
    qr_data: str

@app.post("/mark-attendance")
async def mark_attendance(data: QRData):
    try:
        roll_no, name, reg_no, dept, extra_info = data.qr_data.split(",", 4)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid QR format")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO attendance (roll_no, name, reg_no, dept, extra_info, date)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (roll_no, name, reg_no, dept, extra_info, date.today()))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return JSONResponse(content={"status": "marked"}, status_code=200)

    conn.close()
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)