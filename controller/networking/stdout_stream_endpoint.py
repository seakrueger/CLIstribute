import queue
import asyncio
import logging
import threading

from database import WorkerDatabase

logger = logging.getLogger("controller")
message_logs = {}

class STDOutServerProtocol:
    worker_db = WorkerDatabase()
 
    def connection_made(self, transport):
        self.transport = transport
    
    def datagram_received(self, data, addr):
        decoded_data = data.decode().rstrip()
        worker_id = decoded_data[-3:]
        message = decoded_data[:-3]

        if message == "<<SOM>>":
            logger.debug(f"Worker {worker_id}: SOM recieved")
            try:
                message_logs.pop(worker_id)
            except KeyError:
                pass

            message_logs[worker_id] = []

        if message == "<<EOM>>":
            logger.debug(f"Worker {worker_id}: EOM recieved")

        message_logs[worker_id].append(message)

        logger.debug(f"Worker {worker_id}: {message}")

    def connection_lost(self, exc):
        pass

async def wait_for_shutdown_sig(signal: threading.Event):
    while not signal.is_set():
        await asyncio.sleep(1)

async def main(shutdown_signal: threading.Event, addr):
    event_loop = asyncio.get_running_loop()

    transport, protocol = await event_loop.create_datagram_endpoint(
        lambda: STDOutServerProtocol(),
        local_addr=addr)

    await wait_for_shutdown_sig(shutdown_signal)
    transport.close()

def start_stdout_endpoint(shutdown_signal: threading.Event, finished_shutdown: queue.Queue, addr):
    logger.info(f"starting {threading.current_thread().name} on {addr}")
    asyncio.run(main(shutdown_signal, addr))

    finished_shutdown.put(threading.current_thread().name)
    logger.info(f"Finished {threading.current_thread().name} thread")
