from enum import Enum

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
    def __init__(self, server_name: str, message_type: MessageType, message: str) -> None:
        self.server_name = server_name
        self.type = message_type
        self.message = message
    
    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

class StatusMessage(Message):
    def __init__(self, server_name: str, message: str, succesful: bool, job_id: int) -> None:
        super().__init__(server_name, MessageType.JOB_STATUS, message)
        self.status = {}
        self.status['succesful'] = succesful
        self.status['job_id'] = job_id

class RequestMessage(Message):
    def __init__(self, server_name: str, message: str, request: bool) -> None:
        super().__init__(server_name, MessageType.REQUEST_JOB, message)
        self.request = {}
        self.request['requested'] = request

class ErrorMessage(Message):
    def __init__(self, server_name: str, message: str, error_type: ErrorType, error_message: str, job_id: int) -> None:
        super().__init__(server_name, MessageType.ERROR, message)
        self.error = {}
        self.error['problem'] = error_type
        self.error['error'] = error_message
        self.error['job_id'] = job_id

class CommandMessage(Message):
    def __init__(self, server_name: str, message: str, command: str, output: bool) -> None:
        super().__init__(server_name, MessageType.COMMAND, message)
        self.command = {}
        self.command['command'] = command
        self.command['capture_output'] = output

class CallbackMessage(Message):
    def __init__(self, server_name: str, message: str, come_back: bool, interval_ms: int) -> None:
        super().__init__(server_name, MessageType.NO_COMMAND, message)
        self.callback = {}
        self.callback['come_back'] = come_back
        self.callback['interval'] = interval_ms