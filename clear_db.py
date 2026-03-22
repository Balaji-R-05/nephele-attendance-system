import sqlite3
from config import config

def clear_database():
    """Clears all records from the attendance table."""
    conn = None
    try:
        conn = sqlite3.connect(config.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM attendance")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='attendance'")
        conn.commit()
        print(f"✅ Success: All records cleared from '{config.DB_NAME}'")
    except sqlite3.OperationalError:
        print("⚠️ Warning: Table 'attendance' does not exist yet. Run main.py first to initialize database.")
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("-" * 40)
    print("Attendance System Database Reset Utility")
    print("-" * 40)
    confirm = input("⚠️ Are you sure you want to clear ALL attendance records? (y/n): ")
    if confirm.lower() == 'y':
        clear_database()
    else:
        print("Operation cancelled. No changes were made.")
