import asyncio

from shared.message import MessageType, CommandMessage
from server_message import MessageHandler
import reader

class JobServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        message_handler = MessageHandler()
        try:
            message = message_handler.reciever.parse(data)
            print(message['type'])
            
            match message['type']:
                case MessageType.JOB_STATUS:
                    response = process_status(message)
                case MessageType.REQUEST_JOB:
                    response = process_request(message)
                    if response:
                        response = message_handler.sender.command(response)
                    else:
                        response = message_handler.sender.no_command()
                case MessageType.ERROR:
                    response = process_error(message) 
                case _:
                    raise NotImplemented
                
            if response:
                self.transport.write(response)
        except ValueError as e:
            self.transport.write(message_handler.sender.failed_to_parse(e))
        except NotImplementedError as e:
            self.transport.write(message_handler.sender.failed_to_find_message_type(e))
        finally:
            self.transport.close()

def process_status(message):
    if message['status']['successful']:
        reader.currently_running.remove((message['server_name'], message['job_id']))
    else:
        pass

def process_request(message):
    if message['request']['requested']:
        return reader.grab_next(message['server_name'])

def process_error(message):
    pass

async def main():
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: JobServerProtocol(),
        '', 8888)

    async with server:
        await server.serve_forever()

def start_server():
    print("starting server")
    asyncio.run(main())