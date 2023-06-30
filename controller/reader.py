from shared.command import Command, CommandStatus
from database import CommandDatabase, ServerDatabase

commands = CommandDatabase()
servers = ServerDatabase()

def read_input():
    while True:
        input_command = input("Command: ")
        command = Command(input_command, CommandStatus.QUEUED, True)
        commands.add_command(command)
        
        print("added command")

def grab_next(server):
    next_command_id = commands.get_next_queued()
    if not next_command_id:
        return

    next_command = commands.get_command(next_command_id)
    
    commands.update_command_status(next_command_id, CommandStatus.STARTING)
    servers.set_job_id(server, next_command_id)

    print("grabbed command")
    return next_command

