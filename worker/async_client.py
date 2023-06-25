import asyncio

from client_message import MessageHandler

class JobClientProtocol(asyncio.Protocol):
    def __init__(self, on_con_lost):
        self.messenger = MessageHandler()
        self.on_con_lost = on_con_lost

    def connection_made(self, transport):
        transport.write(self.messenger.sender.request_work())
        print('Data sent')

    def data_received(self, data):
        try:
            response = self.messenger.reciever.parse(data)
        except ValueError as value_error:
            raise value_error
        
        print(response)

    def connection_lost(self, exc):
        print('The server closed the connection')
        self.on_con_lost.set_result(True)

async def main():
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    on_con_lost = loop.create_future()

    transport, protocol = await loop.create_connection(
        lambda: JobClientProtocol(on_con_lost),
        '192.168.1.47', 8888)

    # Wait until the protocol signals that the connection
    # is lost and close the transport.
    try:
        await on_con_lost
    finally:
        transport.close()

asyncio.run(main())