import asyncio

from shared.message import MessageType 
from shared.command import CommandStatus
from server_message import MessageHandler
import reader

class JobServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))

        ip = peername[0]
        self.worker_id = reader.workers.get_worker_id_by_ip(ip)
        if not self.worker_id:
            reader.workers.add_worker(ip, "test <FIXED WITH PROPER HANDSHAKE>", "online <wip>")
            self.worker_id = reader.workers.get_worker_id_by_ip(ip)

        self.transport = transport

    def data_received(self, data):
        message_handler = MessageHandler()
        try:
            message = message_handler.reciever.parse(data)
            print(message['type'])
            
            match message['type']:
                case MessageType.JOB_STATUS:
                    response = self.process_status(message)
                case MessageType.REQUEST_JOB:
                    next_command = self.process_request(message)
                    if next_command:
                        response = message_handler.sender.command(next_command)
                    else:
                        response = message_handler.sender.no_command()
                case MessageType.ERROR:
                    response = self.process_error(message) 
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
    
    def process_status(self, message):
        if message['status']['successful']:
            reader.commands.update_command_status(message['status']['job_id'], CommandStatus.FINISHED)
        else:
            reader.commands.update_command_status(message['status']['job_id'], CommandStatus.FAILED)
        reader.workers.clear_job_id(self.worker_id)

    def process_request(self, message):
        if message['request']['requested']:
            return reader.grab_next(self.worker_id)

    def process_error(self, message):
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
