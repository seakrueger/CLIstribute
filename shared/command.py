from enum import Enum

class CommandStatus(str, Enum):
    QUEUED = 'queued'
    STARTING = 'starting'
    RUNNING = 'running'
    FINISHED = 'finished'
    SUCCESSFUL = 'successful'
    FAILED = 'failed'

class Command():
    def __init__(self, cmd, status: CommandStatus, capture_stdout, job_id=0):
        self.cmd = cmd
        self.status = status
        self.capture_std_out = capture_stdout
        self.job_id = job_id

