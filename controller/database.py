import sqlite3

from shared.command import Command, CommandStatus

class Database():
    def _connect(self):
        self.db_con = sqlite3.connect("clistribute.db")
        self.db_con.row_factory = sqlite3.Row

        self.cursor = self.db_con.cursor()

    def _close(self):
        self.db_con.commit()
        self.db_con.close()
 
class CommandDatabase(Database):
    def add_command(self, command: Command):
        self._connect()

        self.cursor.execute(f"""INSERT INTO commands (command, status, capture_stdout)
                                VALUES('{command.executed_command}', '{command.status}', {command.capture_std_out});
                            """)

        self._close()

    def update_command_status(self, job_id, status: CommandStatus):
        self._connect()

        self.cursor.execute(f"""UPDATE commands
                                SET status = '{status}'
                                WHERE job_id = {job_id};
                            """)
    
        self._close()

    def get_command(self, job_id):
        self._connect()

        self.cursor.execute(f"""SELECT * FROM commands
                                WHERE job_id = {job_id};
                            """)
        result = self.cursor.fetchone()

        self._close()

        result_command = Command(command=result[1],
                                 status=result[2],
                                 capture_stdout=result[3],
                                 job_id=result[0]
                                )
        return result_command

    def get_next_queued(self):
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

class WorkerDatabase(Database):
    def add_worker(self, ip, worker_hostname, status):
        self._connect()

        self.cursor.execute(f"""INSERT INTO workers (ip, name, status)
                                VALUES('{ip}', '{worker_hostname}', '{status}');
                            """)

        self._close()
    
    def update_worker_init(self, worker_id, hostname, status):
        self._connect()

        self.cursor.execute(f"""UPDATE workers
                                SET name = '{hostname}', status = '{status}'
                                WHERE worker_id = {worker_id};
                            """)

        self._close()
 
    def set_status(self, worker_id, status):
        self._connect()

        self.cursor.execute(f"""UPDATE workers
                                SET status = '{status}'
                                WHERE worker_id = {worker_id};
                            """)

        self._close()

    def set_job_id(self, worker_id, job_id):
        self._connect()

        self.cursor.execute(f"""UPDATE workers
                                SET current_job_id = {job_id}
                                WHERE worker_id = {worker_id};
                            """)

        self._close()
    
    def clear_job_id(self, worker_id):
        self._connect()

        self.cursor.execute(f"""UPDATE workers
                                SET current_job_id = NULL
                                WHERE worker_id = {worker_id}
                            """)

        self._close()

    def get_worker_id_by_ip(self, ip):
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

commands = CommandDatabase()
workers = WorkerDatabase()
