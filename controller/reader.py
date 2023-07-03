import queue
import asyncio
import logging
import threading
from aioconsole import ainput

from shared.command import Command, CommandStatus
from database import CommandDatabase

logger = logging.getLogger("controller")

async def read_input(shutdown_signal: threading.Event, finished_shutdown: queue.Queue):
    commands_db = CommandDatabase()

    print("Command: ", end='', flush=True)
    while not shutdown_signal.is_set():
        try:
            input_command = await asyncio.wait_for(ainput(""), 1)
            
            command = Command(input_command, CommandStatus.QUEUED, True)
            commands_db.add_command(command)
            print("Command: ", end='', flush=True)
        except:
            pass
                
    finished_shutdown.put(threading.current_thread().name)
    logger.info(f"Finished {threading.current_thread().name} thread")

def start_reader(shutdown_signal: threading.Event, finished_shutdown: queue.Queue):
    logger.info(f"starting {threading.current_thread().name}")
    asyncio.run(read_input(shutdown_signal, finished_shutdown))
