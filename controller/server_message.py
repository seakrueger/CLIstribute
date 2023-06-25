import socket
import json

from shared.message import CallbackMessage, CommandMessage, ErrorMessage, ErrorType 

class MessageHandler():
    def __init__(self) -> None:
        self.sender = _Sender()
        self.reciever = _Reciever()

class _Sender():
    def __init__(self) -> None:
        self.hostname = socket.gethostname()

    def command(self, command):
        message = CommandMessage(self.hostname, "Command to run", command, True)
        return self._encode(message)

    def no_command(self):
        message = CallbackMessage(self.hostname, "No command right now, come back later", True, 10000)
        return self._encode(message)

    def failed_to_parse(self, exception):
        message = ErrorMessage(self.hostname, "Could not parse to JSON", ErrorType.JSON, exception, 1234)
        return self._encode(message)

    def failed_to_find_message_type(self, exception):
        message = ErrorMessage(self.hostname, "Could not parse msesage type", ErrorType.COMMAND, exception, 1234)
        return self._encode(message)

    def _encode(self, data):
        return json.dumps(data.__dict__).encode()

class _Reciever():
    def parse(self, data):
        try:
            return self._decode(data)
        except ValueError as e:
            raise e

    def _decode(self, data):
        try:
            result = json.loads(data)
            return result
        except ValueError as e:
            raise e