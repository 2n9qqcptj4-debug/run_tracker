import sqlite3
import pandas as pd

DB_PATH = "run_log.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            run_type TEXT,
            distance REAL,
            duration TEXT,
            avg_pace TEXT,
            avg_hr REAL,
            max_hr REAL,
            cadence REAL,
            elevation REAL,
            effort INTEGER,
            weather TEXT,
            terrain TEXT,
            felt TEXT,
            pain TEXT,
            sleep TEXT,
            stress TEXT,
            hydration TEXT,
            vo2max REAL,
            training_load REAL,
            hrv REAL,
            performance_condition TEXT,
            notes TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def add_run(data: dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))

    sql = f"INSERT INTO runs ({columns}) VALUES ({placeholders})"
    c.execute(sql, list(data.values()))

    conn.commit()
    conn.close()


def fetch_runs():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM runs ORDER BY date ASC", conn)
    conn.close()
    return df
