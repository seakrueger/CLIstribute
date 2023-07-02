import sys
import time
import queue
import signal
import sqlite3
import threading

from async_server import start_server
from reader import start_reader

class ControllerApp():
    def __init__(self) -> None:
        self.shutdown = False
        self.shutdown_signal = threading.Event()
        self.finished_shutdown = queue.Queue(2)
        signal.signal(signal.SIGINT, self._exit_handler)
        signal.signal(signal.SIGTERM, self._exit_handler)

        self._init_database()
    
    def start(self):
        i = threading.Thread(target=start_reader, args=(self.shutdown_signal,self.finished_shutdown,), daemon=True, name="Input")
        i.start()

        o = threading.Thread(target=start_server, args=(self.shutdown_signal,self.finished_shutdown,), daemon=True, name="Output")
        o.start()
    
    def run(self):
        pass

    def _exit_handler(self, signal_num, frame):
        if signal_num == 15:
            print("Terminating")
            sys.exit(1)

        print(f"Shutdown signal recieved: {signal_num}")
        self.shutdown_signal.set()
        while not self.finished_shutdown.full():
            print(f"Safely shutdown services: {list(self.finished_shutdown.queue)}")
            time.sleep(0.25)

        print(f"Safely shutdown services: {list(self.finished_shutdown.queue)}")
        self.shutdown = True

    def _init_database(self):
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
    controller = ControllerApp()

    controller.start()
    while not controller.shutdown:
        controller.run()
        time.sleep(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
