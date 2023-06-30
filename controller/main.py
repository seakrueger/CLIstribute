import sqlite3
import threading

from async_server import start_server
from reader import read_input

def init_database():
    db_con = sqlite3.connect("clistribute.db")
    cursor = db_con.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS commands (
                        job_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        command TEXT NOT NULL,
                        status TEXT NOT NULL,
                        capture_stdout INTEGER
                    )
    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS workers (
                        worker_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip TEXT NOT NULL,
                        name TEXT NOT NULL,
                        status TEXT NOT NULL,
                        current_job_id INTEGER 
                    )
    """)

    db_con.commit()
    db_con.close()

def main():
    init_database()

    i = threading.Thread(target=read_input, args=(), name="Input")
    i.start()

    o = threading.Thread(target=start_server, args=(), name="Output")
    o.start()
    o.join()

if __name__ == "__main__":
    main()
