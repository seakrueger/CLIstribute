import asyncio

from shared.message_handler import MessageHandler
from shared.message import MessageType, ErrorType, ErrorMessage, CommandMessage, CallbackMessage, InitMessage 
from shared.command import CommandStatus
from reader import grab_next
import database

class JobServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print(f"Connection from {peername}")

        ip = peername[0]
        self.worker_id = database.workers.get_worker_id_by_ip(ip)
        if not self.worker_id:
            database.workers.add_worker(ip, "Awaiting initialization", "connecting")
            self.worker_id = database.workers.get_worker_id_by_ip(ip)

        self.message_handler = MessageHandler()
        self.transport = transport

    def data_received(self, data):
        try:
            message = self.message_handler.reciever.parse(data)
            print(message['type'])
            
            match message['type']:
                case MessageType.INIT:
                    response = self.process_init(message)
                case MessageType.JOB_STATUS:
                    response = self.process_status(message)
                case MessageType.REQUEST_JOB:
                    response = self.process_request(message)
                case MessageType.ERROR:
                    response = self.process_error(message) 
                case _:
                    raise NotImplemented
            if response:
                self.transport.write(response)

        except ValueError as e:
            response = ErrorMessage("Failed to parse message JSON", ErrorType.JSON, e)
            self.transport.write(self.message_handler.sender.process(response))
        except NotImplementedError as e:
            response = ErrorMessage(f"Failed to find message of type {message['type']}", ErrorType.COMMAND, e)
            self.transport.write(self.message_handler.sender.process(response))
        finally:
            self.transport.close()
    
    def process_init(self, message):
        database.workers.update_worker_init(self.worker_id, message['init']['hostname'], message['init']['status'])
        response = InitMessage("Assigned Worker ID", worker_id=self.worker_id)
        return self.message_handler.sender.process(response)
    
    def process_status(self, message):
        if message['status']['successful']:
            database.commands.update_command_status(message['status']['job_id'], CommandStatus.FINISHED)
        else:
            database.commands.update_command_status(message['status']['job_id'], CommandStatus.FAILED)
        database.workers.clear_job_id(self.worker_id)

    def process_request(self, message):
        if message['request']['requested']:
            next_command = grab_next(self.worker_id)
            if next_command:
                response = CommandMessage("Command to be run", next_command)
            else:
                response = CallbackMessage("No command right now, come back later", True, 10000)
                
            return self.message_handler.sender.process(response)
        else:
            database.workers.set_status(self.worker_id, "not-accepting-work")
        
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
