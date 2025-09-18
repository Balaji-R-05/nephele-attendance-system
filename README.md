# NEPHELE 3.0 ATTENDANCE SYSTEM

This project is a **QR Code-based attendance system** with a minimal HTML frontend and a FastAPI + SQLite backend.  
The frontend scans QR codes in real-time using the device camera and `jsQR`, then sends the data to the backend to mark attendance.

---

## ⚙️ Features
- 🎥 **Camera-based QR Scanner** (using `jsQR`)
- 🔗 **Frontend–Backend Integration** with Fetch API
- 📅 **Attendance Tracking** with date-wise uniqueness
- ✅ **Real-time Status Updates** (scanning, marked, already marked, error)
- 🗄️ **SQLite Database** for lightweight storage

---

## 🖥️ Frontend
- Built with **HTML, CSS, JavaScript**
- Uses `navigator.mediaDevices` to access the camera
- Detects QR codes → sends data to backend
- Displays live feedback:
  - Scanning...
  - Attendance Marked ✅
  - Already Marked ⚠️
  - Server Error ❌ 
- If error, redirects to `/`. 

---

## 🚀 Backend
- **FastAPI** server with CORS enabled
- **SQLite** database with `attendance` table
- API endpoint:  
  - `POST /mark-attendance` → Accepts QR data and records attendance  
- Prevents duplicate marking for the same day