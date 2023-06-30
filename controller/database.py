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

        self.cursor.execute(""" INSERT INTO commands (command, status, capture_stdout)
                                VALUES('{}', '{}', {});
                            """.format(command.executed_command, command.status, command.capture_std_out))

        self._close()

    def update_command_status(self, job_id, status: CommandStatus):
        self._connect()

        self.cursor.execute(""" UPDATE commands
                                SET status = '{}'
                                WHERE job_id = {};
                            """.format(status, job_id))
    
        self._close()

    def get_command(self, job_id):
        self._connect()

        self.cursor.execute(""" SELECT * FROM commands
                                WHERE job_id = {};
                            """.format(job_id))
        result = self.cursor.fetchone()

        self._close()

        result_command = Command(result[1], result[2], result[3], result[0])
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

class ServerDatabase(Database):
    def add_server(self, ip, server_hostname, status):
        self._connect()

        self.cursor.execute(""" INSERT INTO servers (ip, name, status)
                                VALUES('{}', '{}', '{}');
                            """.format(ip, server_hostname, status))

        self._close()

    def set_job_id(self, server_id, job_id):
        self._connect()

        self.cursor.execute(""" UPDATE servers
                                SET current_job_id = {}
                                WHERE server_id = {}
                            """.format(job_id, server_id))

        self._close()
    
    def clear_job_id(self, server_id):
        self._connect()

        self.cursor.execute(""" UPDATE servers
                                SET current_job_id = NULL
                                WHERE server_id = {}
                            """.format(server_id))

        self._close()

    def get_server_id_by_ip(self, ip):
        self._connect()

        self.cursor.execute(""" SELECT server_id FROM servers
                                WHERE ip = '{}'
                                ORDER BY server_id ASC
                                LIMIT 1;
                            """.format(ip))
        result = self.cursor.fetchone()

        self._close()

        if not result:
            return
        return result[0]
