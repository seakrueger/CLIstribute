import socket
import json

from shared.message import ErrorMessage, ErrorType, RequestMessage, StatusMessage

class MessageHandler():
    def __init__(self) -> None:
        self.sender = _Sender()
        self.reciever = _Reciever()

class _Sender():
    def __init__(self) -> None:
        self.hostname = socket.gethostname()

    def job_completed(self):
        message = StatusMessage(self.hostname, "Job Completed", True, 1234)
        return self._encode(message)
    
    def request_work(self):
        message = RequestMessage(self.hostname, "Requesting Work", True)
        return self._encode(message)
    
    def failed_to_parse(self):
        message = ErrorMessage(self.hostname, "Could not parse to JSON", ErrorType.JSON, "Test", 1234)
        return self._encode(message)

    def failed_to_run(self):
        message = ErrorMessage(self.hostname, "Failed to run command", ErrorType.COMMAND, "Test", 1234)
        return self._encode(message)

    def _encode(self, data):
        return json.dumps(data.__dict__).encode()

class _Reciever():
    def parse(self, data):
        return self._decode(data)
   
    def _decode(self, data):
        try:
            result = json.loads(data)
            return result
        except ValueError as e:
            raise e