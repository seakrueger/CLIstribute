import sqlite3
import queue

from command import Command
from database import CommandDatabase

commands = CommandDatabase()
command_queue = queue.Queue()
currently_running = []

def read_input():
    while True:
        input_command = input("Command: ")
        command = Command(input_command, "queued", True)
        commands.add_command(command)
        commands.update_command_status(4, "starting")
        
        next_job = commands.get_next_queued()
        print(commands.get_command(next_job).executed_command)

        print("added command")

def grab_next(server):
    next_command_id = commands.get_next_queued()
    if not next_command_id:
        return

    next_command = commands.get_command(next_command_id)
    
    commands.update_command_status(next_command_id, 'starting')
    currently_running.append((server, next_command.executed_command))

    print("grabbed command")
    return next_command.executed_command

