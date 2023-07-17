import socket
import json

from shared.message import Message

class MessageHandler():
    def __init__(self) -> None:
        self.sender = _Sender()
        self.reciever = _Reciever()

class _Sender():
    def __init__(self) -> None:
        self.hostname = socket.gethostname()
    
    def process(self, worker_id, message: Message):
        message.append_server_id(worker_id)
        message.append_hostname(self.hostname)
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