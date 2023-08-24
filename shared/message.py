from enum import Enum

from shared.command import Command, CommandStatus

class ErrorType(str, Enum):
    JSON = 'json'
    COMMAND = 'command'

class MessageType(str, Enum):
    INIT = 'init'
    JOB_STATUS = 'job_status'
    REQUEST_JOB = 'request_job'
    NO_COMMAND = 'no_command'
    COMMAND = 'command'
    ERROR = 'error'
    PING = 'ping'
    SHUTDOWN = 'shutdown'

class Message(object):
    def __init__(self, message_type: MessageType, message: str) -> None:
        self.type = message_type
        self.message = message

    def append_hostname(self, hostname):
        self.hostname = hostname
    
    def append_server_id(self, worker_id):
        self.worker_id = worker_id
    
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

class InitMessageToController(Message):
    def __init__(self, message: str, hostname: str, status: str) -> None:
        super().__init__(MessageType.INIT, message)
        self.init = {}
        self.init['hostname'] = hostname
        self.init['status'] = status

class InitFromControllerMessage(Message):
    def __init__(self, message: str, worker_id: int, packages) -> None:
        super().__init__(MessageType.INIT, message)
        self.init = {}
        self.init['worker_id'] = worker_id
        self.init['packages'] = packages

class StatusMessage(Message):
    def __init__(self, message: str, status: CommandStatus, successful: bool, job_id: int) -> None:
        super().__init__(MessageType.JOB_STATUS, message)
        self.status = {}
        self.status['status'] = status
        self.status['successful'] = successful
        self.status['job_id'] = job_id

class RequestMessage(Message):
    def __init__(self, message: str, request: bool) -> None:
        super().__init__(MessageType.REQUEST_JOB, message)
        self.request = {}
        self.request['requested'] = request

class ErrorMessage(Message):
    def __init__(self, message: str, error_type: ErrorType, error_message: str, job_id: int = None) -> None:
        super().__init__(MessageType.ERROR, message)
        self.error = {}
        self.error['problem'] = error_type
        self.error['error'] = error_message
        self.error['job_id'] = job_id

class CommandMessage(Message):
    def __init__(self, message: str, command: Command) -> None:
        super().__init__(MessageType.COMMAND, message)
        self.command = {}
        self.command['cmd'] = command.cmd
        self.command['capture_output'] = command.capture_std_out
        self.command['job_id'] = command.job_id

class CallbackMessage(Message):
    def __init__(self, message: str, come_back: bool, interval: int) -> None:
        super().__init__(MessageType.NO_COMMAND, message)
        self.callback = {}
        self.callback['come_back'] = come_back
        self.callback['interval'] = interval

class PingMessage(Message):
    def __init__(self, message) -> None:
        super().__init__(MessageType.PING, message)

class ShutdownMessage(Message):
    def __init__(self, finished: bool, job_id: int = None):
        super().__init__(MessageType.SHUTDOWN, "Shutting down")
        self.shutdown = {}
        self.shutdown['finished'] = finished
        self.shutdown['job_id'] = job_id