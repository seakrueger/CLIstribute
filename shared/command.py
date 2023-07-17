from enum import Enum

class CommandStatus(str, Enum):
    QUEUED = 'queued'
    STARTING = 'starting'
    RUNNING = 'running'
    FINISHED = 'finished'
    FAILED = 'failed'

class Command():
    def __init__(self, command, args, status: CommandStatus, capture_stdout, job_id=0):
        self.executed_command = command
        self.args = args
        self.status = status
        self.capture_std_out = capture_stdout
        self.job_id = job_id

