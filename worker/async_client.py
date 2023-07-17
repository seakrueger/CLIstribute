import asyncio
import socket
import sys

from shared.message_handler import MessageHandler
from shared.message import Message, RequestMessage, InitMessage

class JobClientProtocol(asyncio.Protocol):
    def __init__(self, on_con_lost, worker_id, message: Message):
        self.messenge_handler = MessageHandler()
        self.message = message
        self.on_con_lost = on_con_lost
        self.worker_id = worker_id

    def connection_made(self, transport):
        transport.write(self.messenge_handler.sender.process(self.worker_id, self.message))
        print('Data sent')

    def data_received(self, data):
        try:
            response = self.messenge_handler.reciever.parse(data)
        except ValueError as value_error:
            raise value_error
        
        self.response = response

    def connection_lost(self, exc):
        print('The server closed the connection')
        self.on_con_lost.set_result(True)

async def send_message(loop, addr, worker_id, message: Message):
    on_con_lost = loop.create_future()
    transport, protocol = await loop.create_connection(
        lambda: JobClientProtocol(on_con_lost, worker_id, message),
        addr[0], addr[1])
    try:
        await on_con_lost
    finally:
        result = protocol.response
        transport.close()
        return result
