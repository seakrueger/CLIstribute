import sys
import queue
import asyncio
import logging
import threading

from shared.command import Command, CommandStatus
from database import CommandDatabase

logger = logging.getLogger("controller")

async def wait_for_shutdown_sig(signal: threading.Event):
    while not signal.is_set():
        await asyncio.sleep(1)

async def asy_input(prompt: str) -> str:
    print(prompt, end='', flush=True)
    event_loop = asyncio.get_running_loop()
    result = await event_loop.run_in_executor(None, lambda: sys.stdin.readline())
    return result.rstrip()

async def read_input(shutdown_signal: threading.Event, finished_shutdown: queue.Queue):
    commands_db = CommandDatabase()

    while not shutdown_signal.is_set():
        done, pending = await asyncio.wait([asy_input("Command: "), wait_for_shutdown_sig(shutdown_signal)], return_when=asyncio.FIRST_COMPLETED) 

        result = list(done)[0].result()
        if result:
            split = result.split()
            ex_command = split[0]
            split.pop(0)
            args = " ".join(split)

            command = Command(ex_command, args, CommandStatus.QUEUED, True)
            commands_db.add_command(command)
        else:
            for task in pending:
                task.cancel()
               
    finished_shutdown.put(threading.current_thread().name)
    logger.info(f"Finished {threading.current_thread().name} thread")

def start_reader(shutdown_signal: threading.Event, finished_shutdown: queue.Queue):
    logger.info(f"starting {threading.current_thread().name}")
    asyncio.run(read_input(shutdown_signal, finished_shutdown))
