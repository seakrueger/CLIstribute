import queue
import asyncio
import logging
import threading

logger = logging.getLogger("controller")

class STDOutServerProtocol:
    def connection_made(self, transport):
        self.transport = transport
    
    def datagram_received(self, data, addr):
        message = data.decode()

async def wait_for_shutdown_sig(signal: threading.Event):
    while not signal.is_set():
        await asyncio.sleep(1)

async def main(shutdown_signal: threading.Event, finished_shutdown: queue.Queue):
    event_loop = asyncio.get_running_loop()

    transport, protocol = await event_loop.create_datagram_endpoint(
        lambda: STDOutServerProtocol(),
        local_addr=('', 9601))

    await wait_for_shutdown_sig(shutdown_signal)
    transport.close()

    finished_shutdown.put(threading.current_thread().name)
    logger.info(f"Finished {threading.current_thread().name} thread")

def start_stdout_endpoint(shutdown_signal: threading.Event, finished_shutdown: queue.Queue):
    logger.info(f"starting {threading.current_thread().name}")
    asyncio.run(main(shutdown_signal, finished_shutdown))
