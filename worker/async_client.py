import asyncio
import socket
import sys

from shared.message_handler import MessageHandler
from shared.message import Message, RequestMessage, InitMessage

class JobClientProtocol(asyncio.Protocol):
    def __init__(self, on_con_lost, message: Message):
        self.messenge_handler = MessageHandler()
        self.message = message
        self.on_con_lost = on_con_lost

    def connection_made(self, transport):
        transport.write(self.messenge_handler.sender.process(self.message))
        print('Data sent')

    def data_received(self, data):
        try:
            response = self.messenge_handler.reciever.parse(data)
        except ValueError as value_error:
            raise value_error
        
        print(response)

    def connection_lost(self, exc):
        print('The server closed the connection')
        self.on_con_lost.set_result(True)

async def send_message(loop, ip, port, message: Message):
    on_con_lost = loop.create_future()
    transport, protocol = await loop.create_connection(
        lambda: JobClientProtocol(on_con_lost, message),
        str(ip), port)
    try:
        await on_con_lost
    finally:
        transport.close()

async def main(ip, port):
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    await send_message(loop, ip, port, InitMessage("Connecting worker to controller", socket.gethostname(), "accepting-work"))

    await send_message(loop, ip, port, RequestMessage("Requesting Work", True))

if __name__ == "__main__":
    args = sys.argv
    if len(args) != 3:
        print("Please provide both an ip and port")
        quit()

    asyncio.run(main(args[1], args[2]))