import sqlite3
import csv
from pathlib import Path

DATA_PATH = Path("cell-count.csv")
DB_PATH = Path("loblaw-database.db")

POPULATIONS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]

def create_tables(connection): 
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS subjects (
            subject_id TEXT PRIMARY KEY, 
            project TEXT NOT NULL, 
            condition TEXT NOT NULL, 
            age INTEGER NOT NULL, 
            sex TEXT NOT NULL,
            treatment TEXT NOT NULL,
            response TEXT);

        CREATE TABLE IF NOT EXISTS samples (
            sample_id TEXT PRIMARY KEY, 
            subject_id TEXT NOT NULL,  
            sample_type TEXT NOT NULL, 
            time_from_treatment_start INTEGER NOT NULL, 
            FOREIGN KEY (subject_id) REFERENCES  subjects(subject_id));

        CREATE TABLE IF NOT EXISTS cell_counts (
            sample_id TEXT NOT NULL, 
            population TEXT NOT NULL, 
            count INTEGER NOT NULL, 
            PRIMARY KEY (sample_id, population), 
            FOREIGN KEY (sample_id) REFERENCES samples(sample_id));
    """)
#IF HAVE TIME COME BACK AND ADD INDEXES

def load_data(connection):
    with DATA_PATH.open(newline="") as file: 
        reader = csv.DictReader(file)
        for row in reader: 
            connection.execute(
                """INSERT OR IGNORE INTO subjects
                    (subject_id, project, condition, age, sex, treatment, response) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)""", (
                        row["subject"], 
                        row["project"], 
                        row["condition"], 
                        int(row["age"]), 
                        row["sex"], 
                        row["treatment"], 
                        row["response"]
                    )
            ) 
            connection.execute(
                """INSERT OR IGNORE INTO samples
                    (sample_id, subject_id, sample_type, time_from_treatment_start)
                    VALUES (?, ?, ?, ?)""", 
                    (
                        row["sample"], 
                        row["subject"],  
                        row["sample_type"], 
                        int(row["time_from_treatment_start"])
                    )
            )
            for population in POPULATIONS: 
                connection.execute(
                    """INSERT OR REPLACE INTO cell_counts 
                        (sample_id, population, count)
                        VALUES (?, ?, ?)""", 
                    (
                        row["sample"], 
                        population,
                        int(row[population])
                    )
                )

def main(): 
    if not DATA_PATH.exists(): 
        raise FileNotFoundError(f"Input file not found: {DATA_PATH}")
    if DB_PATH.exists(): 
        DB_PATH.unlink()
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON") 
        create_tables(connection)
        load_data(connection)
    print(f"Database created: {DB_PATH}")

if __name__ == "__main__":
    main()