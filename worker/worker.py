import sys
import shlex
import socket
import asyncio

import async_client
import stdout_stream
from shared.message import InitMessage, RequestMessage, StatusMessage, MessageType
from shared.command import CommandStatus

class Worker():
    def __init__(self, ip):
        self.loop = asyncio.get_running_loop()
        self.ip = ip
        self.addr = (ip, 9600)

    def set_id(self, worker_id):
        self.worker_id = worker_id
        self.streamer = stdout_stream.Sender((self.ip, 9601), self.worker_id)

    async def init_connect(self):
        return await async_client.send_message(self.loop, self.addr, -1, InitMessage("Connecting worker to controller", socket.gethostname(), "accepting-work"))

    async def request_work(self):
        return await async_client.send_message(self.loop, self.addr, self.worker_id, RequestMessage("Requesting Work", True))

    async def execute_work(self, work):
        self.command = work["command"]
        try:
            cmd = shlex.split(self.command["cmd"])
            process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.STDOUT)

            await self._send_status("Running Job", CommandStatus.RUNNING, False)

            full_log = b""
            while process.returncode is None:
                buf = await process.stdout.read(20)
                if not buf:
                    break
                full_log += buf
                self.streamer.send(buf)

            if process.returncode == 0 or process.returncode is None: 
                await self._send_status("Job Finished", CommandStatus.FINISHED, True)
            else:
                await self._send_status("Job Failed", CommandStatus.FINISHED, False)
        except:
            await self._send_status("Job Failed", CommandStatus.FINISHED, False)

    async def _send_status(self, message, status, success):
        await async_client.send_message(self.loop, self.addr, self.worker_id, StatusMessage(message, status, success, self.command["job_id"]))

async def main(*args):
    worker = Worker(args[0][1])

    response = await worker.init_connect()
    worker.set_id(response["init"]["worker_id"])

    while True:
        work = await worker.request_work()

        if work["type"] == MessageType.NO_COMMAND:
            if work["callback"]["come_back"]:
                await asyncio.sleep(work["callback"]["interval"] / 1000)
                continue

        await worker.execute_work(work)

if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2:
        print("Please provide an ip address to connect to")
        quit()

    asyncio.run(main(args))