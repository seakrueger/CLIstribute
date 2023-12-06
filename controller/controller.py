import os
import time
import queue
import signal
import socket
import sqlite3
import logging
import threading

import toml

from networking.worker_handler_server import start_handler_server
from networking.stdout_stream_endpoint import start_stdout_endpoint
from ui.web_server import start_webapp
from ui.basic import start_reader

logger = logging.getLogger("controller")

class ControllerApp():
    def __init__(self, args) -> None:
        self.args = args

        self.shutdown = False
        self.shutdown_signal = threading.Event()
        self.finished_shutdown = queue.Queue(3)
        signal.signal(signal.SIGINT, self._exit_handler)
        signal.signal(signal.SIGTERM, self._exit_handler)

        self._load_config()
        self._init_database()
        self._resolve_local_ip()
    
    def start(self):
        if self.args.webapp:
            webapp_thread = threading.Thread(target=start_webapp, args=(self.shutdown_signal, self.finished_shutdown, (self.ip, 9600), self.config,), daemon=True, name="WebApp")
            webapp_thread.start()
        else:
            reader_thread = threading.Thread(target=start_reader, args=(self.shutdown_signal, self.finished_shutdown, self.config,), daemon=True, name="UserInputThread")
            reader_thread.start()

        handler_thread = threading.Thread(target=start_handler_server, args=(self.shutdown_signal, self.finished_shutdown, (self.ip, 9601), self.config,), daemon=True, name="WorkerHandlerThread")
        handler_thread.start()

        stdout_thread = threading.Thread(target=start_stdout_endpoint, args=(self.shutdown_signal, self.finished_shutdown, (self.ip, 9602), self.config), daemon=True, name="StdOutStreamThread")
        stdout_thread.start()
    
    def run(self):
        pass

    def _exit_handler(self, signal_num, frame):
        logger.warning(f"Shutdown signal recieved")
        self.shutdown_time = time.time()
        self.shutdown_signal.set()
        while not self.finished_shutdown.full():
            logger.debug(f"Safely shutdown services: {list(self.finished_shutdown.queue)}")
            time.sleep(0.25)

        logger.info(f"Safely shutdown services: {list(self.finished_shutdown.queue)}")
        self.shutdown = True

    def _init_database(self):
        logger.debug("Creating database and tables")

        db_path = os.getenv("CLISTRIBUTE_DB", "clistribute.db")
        db_con = sqlite3.connect(db_path)
        cursor = db_con.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS commands (
                            job_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            cmd TEXT NOT NULL,
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

    def _load_config(self):
        config_path = os.getenv("CONFIG_PATH", "resources/")
        config_name = os.getenv("CONFIG_FILE", "config.toml")
        try:
            with open(os.path.join(config_path, config_name)) as config_file:
                self.config = toml.load(config_file)
            logger.info("Loading custom config")
        except FileNotFoundError:
            logger.warning("Loading default config")
            with open("/clistribute/resources/config.toml") as config_file:
                self.config = toml.load(config_file)

        logger.debug("Loaded config file")

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

        self.ip = ip
