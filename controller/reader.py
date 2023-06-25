import queue

command_queue = queue.Queue()
currently_running = []

def read_input():
    while True:
        command = input("Command: ")
        command_queue.put(command)
        print("added command")

def grab_next(server):
    try:
        command = command_queue.get(block=False)    
    except queue.Empty:
        return

    currently_running.append((server, command))
    print("grabbed command")
    return command