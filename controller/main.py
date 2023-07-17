import sys
import time
import queue
import signal
import socket
import sqlite3
import logging
import threading
from logging.handlers import RotatingFileHandler

from networking.worker_handler_server import start_handler_server
from networking.stdout_stream_endpoint import start_stdout_endpoint
from reader import start_reader

class ControllerApp():
    def __init__(self) -> None:
        self.shutdown = False
        self.shutdown_signal = threading.Event()
        self.finished_shutdown = queue.Queue(3)
        signal.signal(signal.SIGINT, self._exit_handler)
        signal.signal(signal.SIGTERM, self._exit_handler)

        self._init_database()
        self.ip = self._resolve_local_ip()
    
    def start(self):
        reader_thread = threading.Thread(target=start_reader, args=(self.shutdown_signal, self.finished_shutdown,), daemon=True, name="UserInputThread")
        reader_thread.start()

        handler_thread = threading.Thread(target=start_handler_server, args=(self.shutdown_signal, self.finished_shutdown, (self.ip, 9600),), daemon=True, name="WorkerHandlerThread")
        handler_thread.start()

        stdout_thread = threading.Thread(target=start_stdout_endpoint, args=(self.shutdown_signal, self.finished_shutdown, (self.ip, 9601),), daemon=True, name="StdOutStreamThread")
        stdout_thread.start()
    
    def run(self):
        pass

    def _exit_handler(self, signal_num, frame):
        logger.debug(f"Shutdown signal recieved: {signal_num}")
        self.shutdown_time = time.time()
        self.shutdown_signal.set()
        while not self.finished_shutdown.full():
            logger.debug(f"Safely shutdown services: {list(self.finished_shutdown.queue)}")
            time.sleep(0.25)

        logger.info(f"Safely shutdown services: {list(self.finished_shutdown.queue)}")
        self.shutdown = True

    def _init_database(self):
        logger.info("Creating database and tables")
        db_con = sqlite3.connect("clistribute.db")
        cursor = db_con.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS commands (
                            job_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            command TEXT NOT NULL,
                            args TEXT NOT NULL,
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

    def _resolve_local_ip(self):
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.settimeout(0)
        try:
            temp_socket.connect(("10.254.254.254", 1))
            ip = temp_socket.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            temp_socket.close()

        return ip

def main():
    controller = ControllerApp()

    controller.start()
    while not controller.shutdown:
        controller.run()
        time.sleep(1)
    else:
        logger.info(f"Shutdown in {(time.time() - controller.shutdown_time):.2f} seconds")
        sys.exit(0)

if __name__ == "__main__":
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter("[%(levelname)s]: %(threadName)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    file_handler = RotatingFileHandler("cli-controller.log", maxBytes = 5*1024*1024, backupCount = 2)
    file_handler.setLevel(logging.WARNING)
    file_formatter = logging.Formatter("%(asctime)s: [%(levelname)s]: %(threadName)s - %(message)s")
    file_handler.setFormatter(file_formatter)

    logger = logging.getLogger("controller")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    main()
