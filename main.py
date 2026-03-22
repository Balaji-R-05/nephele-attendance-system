from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sqlite3
from datetime import date
from contextlib import asynccontextmanager
from typing import Optional, List
from config import config
import os

def get_db_connection():
    conn = sqlite3.connect(config.DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT NOT NULL,
        name TEXT NOT NULL,
        reg_no TEXT NOT NULL,
        dept TEXT NOT NULL,
        extra_info TEXT,
        date TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(roll_no, date)
    )
    """)
    conn.commit()
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if config.DEBUG:
        print(f"🚀 Starting up... Initializing DB: {config.DB_NAME}")
    init_db()
    yield
    if config.DEBUG:
        print("🛑 Shutting down...")

app = FastAPI(lifespan=lifespan, title="QR Attendance System (Nephele 3.0 Test)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QRData(BaseModel):
    qr_data: str = Field(..., description="Comma separated or JSON string containing roll_no, name, reg_no, dept, extra_info")

class AttendanceRecord(BaseModel):
    id: int
    roll_no: str
    name: str
    reg_no: str
    dept: str
    extra_info: Optional[str]
    date: str
    timestamp: str

@app.get("/", response_class=FileResponse)
async def get_scanner():
    return FileResponse("main.html")

@app.get("/admin", response_class=FileResponse)
async def get_admin():
    return FileResponse("admin.html")

@app.post("/mark-attendance")
async def mark_attendance(data: QRData):
    try:
        if data.qr_data.startswith("{"):
            import json
            parsed = json.loads(data.qr_data)
            roll_no = parsed.get("roll_no")
            name = parsed.get("name")
            reg_no = parsed.get("reg_no")
            dept = parsed.get("dept")
            extra_info = parsed.get("extra_info", "")
        else:
            parts = data.qr_data.split(",")
            if len(parts) < 4:
                raise ValueError("Insufficient data fields")
            roll_no, name, reg_no, dept = parts[:4]
            extra_info = parts[4] if len(parts) > 4 else ""
            
        if not all([roll_no, name, reg_no, dept]):
            raise ValueError("Missing required fields")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid QR format: {str(e)}")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO attendance (roll_no, name, reg_no, dept, extra_info, date)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (roll_no, name, reg_no, dept, extra_info, date.today().isoformat()))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return JSONResponse(content={"status": "marked"}, status_code=200)
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

    conn.close()
    return {"status": "success"}

@app.get("/attendance", response_model=List[AttendanceRecord])
async def get_attendance(date_filter: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM attendance"
    params = []
    
    if date_filter:
        query += " WHERE date = ?"
        params.append(date_filter)
    
    query += " ORDER BY timestamp DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=config.DEBUG)