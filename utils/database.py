import sqlite3
import pandas as pd

DB_PATH = "run_log.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
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
    conn = get_conn()
    c = conn.cursor()
    cols = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    sql = f"INSERT INTO runs ({cols}) VALUES ({placeholders})"
    c.execute(sql, list(data.values()))
    conn.commit()
    conn.close()


def update_run(run_id: int, data: dict):
    conn = get_conn()
    c = conn.cursor()
    assignments = ", ".join([f"{k} = ?" for k in data.keys()])
    sql = f"UPDATE runs SET {assignments} WHERE id = ?"
    values = list(data.values()) + [run_id]
    c.execute(sql, values)
    conn.commit()
    conn.close()


def delete_run(run_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM runs WHERE id = ?", (run_id,))
    conn.commit()
    conn.close()


def fetch_runs():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM runs ORDER BY date ASC", conn)
    conn.close()
    return df
