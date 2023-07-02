from shared.command import Command, CommandStatus
import database

def read_input():
    while True:
        input_command = input("Command: ")
        command = Command(input_command, CommandStatus.QUEUED, True)
        database.commands.add_command(command)
        
        print("added command")

