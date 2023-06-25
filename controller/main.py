import sqlite3
import threading

from reader import read_input
from async_server import start_server

def init_database():
    db_con = sqlite3.connect("clistribute.db")
    cursor = db_con.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS commands (
                        job_id INTEGER NOT NULL PRIMARY KEY,
                        command TEXT NOT NULL,
                        capture_stdout INTEGER
                    )
    """)

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