import sqlite3
import pandas as pd


DB_PATH = "run_log.db"




def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn




def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
"""
CREATE TABLE IF NOT EXISTS runs (
id INTEGER PRIMARY KEY AUTOINCREMENT,
date TEXT NOT NULL,
run_type TEXT,
distance REAL,
duration_minutes REAL,
avg_pace TEXT,
avg_hr INTEGER,
max_hr INTEGER,
cadence INTEGER,
elevation_gain INTEGER,
effort INTEGER,
how_felt TEXT
)
"""
)
    conn.commit()
    conn.close()




def fetch_runs():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM runs ORDER BY date ASC", conn)
    conn.close()
    return df