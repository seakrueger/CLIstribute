class Command():
    def __init__(self, command, status, capture_stdout, job_id=0):
        self.executed_command = command
        self.status = status
        self.capture_std_out = capture_stdout

