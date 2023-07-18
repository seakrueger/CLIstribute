import asyncio
import logging

from shared.message_handler import MessageHandler
from shared.message import Message

logger = logging.getLogger("worker")

class JobClientProtocol(asyncio.Protocol):
    def __init__(self, on_con_lost, worker_id, message: Message):
        self.messenge_handler = MessageHandler()
        self.message = message
        self.on_con_lost = on_con_lost
        self.worker_id = worker_id

    def connection_made(self, transport):
        transport.write(self.messenge_handler.sender.process(self.worker_id, self.message))
        logger.debug(f"Data sent: {self.message}")

    def data_received(self, data):
        try:
            response = self.messenge_handler.reciever.parse(data)
        except ValueError as value_error:
            raise value_error
        
        self.response = response
        logger.debug(f"Data recieved: {self.response}")

    def connection_lost(self, exc):
        logger.debug('The server closed the connection')
        self.on_con_lost.set_result(True)

async def send_message(loop, addr, worker_id, message: Message):
    on_con_lost = loop.create_future()

    transport, protocol = await loop.create_connection(
        lambda: JobClientProtocol(on_con_lost, worker_id, message),
        addr[0], addr[1])

    try:
        await on_con_lost
    finally:
        try:
            result = protocol.response
        except AttributeError:
            result = None
        finally:
            transport.close()
        return result
