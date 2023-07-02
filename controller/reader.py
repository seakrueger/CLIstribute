import time
import queue
import asyncio
import threading

from aioconsole import ainput
from shared.command import Command, CommandStatus
import database

async def read_input(shutdown_signal: threading.Event, finished_shutdown: queue.Queue):
    while not shutdown_signal.is_set():
        input_command = await ainput("Command: ")
        command = Command(input_command, CommandStatus.QUEUED, True)
        database.commands.add_command(command)
        
        print("added command")
        
    finished_shutdown.put(threading.current_thread().name)
    print(f"Finished {threading.current_thread().name} thread")

def start_reader(shutdown_signal: threading.Event, finished_shutdown: queue.Queue):
    print("starting reader")
    asyncio.run(read_input(shutdown_signal, finished_shutdown))

