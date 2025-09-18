from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
import sqlite3
import cv2
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "attendance.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT NOT NULL,
        name TEXT NOT NULL,
        reg_no TEXT NOT NULL,
        dept TEXT NOT NULL,
        extra_info TEXT,
        date DATE NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(roll_no, date)
    )
    """)
    conn.commit()
    conn.close()

init_db()

def extract_qr_from_image(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(img)

    if not data:
        return None
    return data

@app.post("/mark-attendance")
async def mark_attendance(file: UploadFile = File(...)):
    image_bytes = await file.read()

    qr_data = extract_qr_from_image(image_bytes)
    if not qr_data:
        return JSONResponse(content={"status": "qr not found"}, status_code=400)

    try:
        roll_no, name, reg_no, dept, extra_info = qr_data.split(",", 4)
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
