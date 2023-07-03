import queue
import asyncio
import logging
import threading

from shared.message_handler import MessageHandler
from shared.message import MessageType, ErrorType, ErrorMessage, CommandMessage, CallbackMessage, InitMessage 
from shared.command import CommandStatus
import database

logger = logging.getLogger("controller")

class JobServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        logger.info(f"Connection from {peername}")

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
            logger.debug(f"Message type: {message['type']}")
            
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
            next_command = database.grab_next(self.worker_id)
            if next_command:
                response = CommandMessage("Command to be run", next_command)
            else:
                response = CallbackMessage("No command right now, come back later", True, 10000)
                
            return self.message_handler.sender.process(response)
        else:
            database.workers.set_status(self.worker_id, "not-accepting-work")
        
    def process_error(self, message):
        pass

async def wait_for_shutdown_sig(signal: threading.Event):
    while not signal.is_set():
        await asyncio.sleep(1)

async def main(shutdown_signal: threading.Event, finished_shutdown: queue.Queue):
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: JobServerProtocol(),
        '', 8888)

    async with server:
        await asyncio.wait([server.serve_forever(), wait_for_shutdown_sig(shutdown_signal)], return_when=asyncio.FIRST_COMPLETED)
    
    finished_shutdown.put(threading.current_thread().name)
    logger.info(f"Finished {threading.current_thread().name} thread")

def start_server(shutdown_signal: threading.Event, finished_shutdown: queue.Queue):
    logger.info(f"starting {threading.current_thread().name}")
    asyncio.run(main(shutdown_signal, finished_shutdown))
