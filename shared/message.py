from enum import Enum

from shared.command import Command

class ErrorType(str, Enum):
    JSON = 'json'
    COMMAND = 'command'

class MessageType(str, Enum):
    JOB_STATUS = 'job_status'
    REQUEST_JOB = 'request_job'
    NO_COMMAND = 'no_command'
    COMMAND = 'command'
    ERROR = 'error'

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

class StatusMessage(Message):
    def __init__(self, message: str, successful: bool, job_id: int) -> None:
        super().__init__(MessageType.JOB_STATUS, message)
        self.status = {}
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
        self.command['command'] = command.executed_command
        self.command['capture_output'] = command.capture_std_out
        self.command['job_id'] = command.job_id

class CallbackMessage(Message):
    def __init__(self, message: str, come_back: bool, interval_ms: int) -> None:
        super().__init__(MessageType.NO_COMMAND, message)
        self.callback = {}
        self.callback['come_back'] = come_back
        self.callback['interval'] = interval_ms
