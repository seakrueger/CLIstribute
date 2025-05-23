import os
import sqlite3
import threading
import logging

from shared.command import Command, CommandStatus

logger = logging.getLogger("controller")

class Database():
    _instance = None
    _lock = threading.Lock()

    db_path = os.getenv("CLISTRIBUTE_DB", "clistribute.db")

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def _connect(self):
        self.db_con = sqlite3.connect(self.db_path)
        self.db_con.row_factory = sqlite3.Row

        self.cursor = self.db_con.cursor()

    def _close(self):
        self.db_con.commit()
        self.db_con.close()
 
class CommandDatabase(Database):
    def add_command(self, command: Command):
        with self._lock:
            self._connect()

            self.cursor.execute(f"""INSERT INTO commands (cmd, status, capture_stdout)
                                    VALUES('{command.cmd}', '{command.status}', {command.capture_std_out});
                                """)

            self._close()
        logger.debug("Added Command to Database")

    def update_command_status(self, job_id, status: CommandStatus):
        with self._lock:
            self._connect()

            self.cursor.execute(f"""UPDATE commands
                                    SET status = '{status}'
                                    WHERE job_id = {job_id};
                                """)
    
            self._close()

    def get_command(self, job_id):
        with self._lock:
            self._connect()

            self.cursor.execute(f"""SELECT * FROM commands
                                    WHERE job_id = {job_id};
                                """)
            result = self.cursor.fetchone()

            self._close()
        logger.debug("Grabbed Command from Database")
        
        result_command = Command(cmd=result[1],
                                 status=result[2],
                                 capture_stdout=result[3],
                                 job_id=result[0]
                                )
        return result_command

    def get_next_queued(self):
        with self._lock:
            self._connect()

            self.cursor.execute(""" SELECT job_id, status FROM commands
                                    WHERE status = 'queued'
                                    ORDER BY job_id ASC
                                    LIMIT 1;
                                """)
            result = self.cursor.fetchone()

            self._close()

        if not result:
            return
        return result[0]

    def get_all_commands(self):
        with self._lock:
            self._connect()

            self.cursor.execute(""" SELECT * FROM commands
                                    ORDER BY job_id DESC
                                """)
            result = self.cursor.fetchall()

            self._close()
        
        return result

class WorkerDatabase(Database):
    def add_worker(self, ip, worker_hostname, status):
        with self._lock:
            self._connect()

            self.cursor.execute(f"""INSERT INTO workers (ip, name, status)
                                    VALUES('{ip}', '{worker_hostname}', '{status}');
                                """)

            self._close()
        logger.debug("Added Worker to Database")
    
    def update_worker_init(self, worker_id, hostname, status):
        with self._lock:
            self._connect()

            self.cursor.execute(f"""UPDATE workers
                                    SET name = '{hostname}', status = '{status}'
                                    WHERE worker_id = {worker_id};
                                """)

            self._close()
        logger.debug("Updated Worker in Database")
 
    def set_status(self, worker_id, status):
        with self._lock:
            self._connect()

            self.cursor.execute(f"""UPDATE workers
                                    SET status = '{status}'
                                    WHERE worker_id = {worker_id};
                                """)

            self._close()

    def set_job_id(self, worker_id, job_id):
        with self._lock:
            self._connect()

            self.cursor.execute(f"""UPDATE workers
                                    SET current_job_id = {job_id}
                                    WHERE worker_id = {worker_id};
                                """)

            self._close()
    
    def clear_job_id(self, worker_id):
        with self._lock:
            self._connect()

            self.cursor.execute(f"""UPDATE workers
                                    SET current_job_id = NULL
                                    WHERE worker_id = {worker_id}
                                """)

            self._close()

    def get_worker_id_by_ip(self, ip):
        with self._lock:
            self._connect()

            self.cursor.execute(f"""SELECT worker_id FROM workers
                                    WHERE ip = '{ip}'
                                    ORDER BY worker_id ASC
                                    LIMIT 1;
                                """)
            result = self.cursor.fetchone()

            self._close()

        if not result:
            return
        return result[0]

    def get_hostname_by_id(self, id):
        with self._lock:
            self._connect()

            self.cursor.execute(f"""SELECT name FROM workers
                                    WHERE worker_id = {id}
                                    LIMIT 1;
                                """)
            result = self.cursor.fetchone()

            self._close()
        
        if not result:
            return
        return result[0]

    def get_all_workers(self):
        with self._lock:
            self._connect()

            self.cursor.execute(""" SELECT * FROM workers
                                    ORDER BY worker_id ASC
                                """)
            result = self.cursor.fetchall()

            self._close()
        
        return result
