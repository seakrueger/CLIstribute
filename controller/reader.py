from shared.command import Command, CommandStatus
import database

def read_input():
    while True:
        input_command = input("Command: ")
        command = Command(input_command, CommandStatus.QUEUED, True)
        database.commands.add_command(command)
        
        print("added command")

def grab_next(worker):
    next_command_id = database.commands.get_next_queued()
    if not next_command_id:
        return

    next_command = database.commands.get_command(next_command_id)
    
    database.commands.update_command_status(next_command_id, CommandStatus.STARTING)
    database.workers.set_job_id(worker, next_command_id)

    print("grabbed command")
    return next_command
