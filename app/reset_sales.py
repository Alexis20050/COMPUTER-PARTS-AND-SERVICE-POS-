import sqlite3
import os

def update_database():
    db_path = "data/app.db"
    
    if not os.path.exists(db_path):
        print("❌ Database not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE sales ADD COLUMN customer_name TEXT DEFAULT ''")
        conn.commit()
        print("✅ customer_name column added!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("✅ customer_name column already exists!")
        else:
            print(f"❌ Error: {e}")
    
    conn.close()

if __name__ == "__main__":
    update_database()
    input("Press Enter to exit...")