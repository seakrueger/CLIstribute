import os
import sys
import shlex
import socket
import asyncio
import logging
from logging.handlers import RotatingFileHandler

import async_client
import stdout_stream
from shared.message import InitMessage, RequestMessage, StatusMessage, MessageType, PingMessage
from shared.command import CommandStatus

class Worker():
    def __init__(self, ip):
        self.loop = asyncio.get_running_loop()
        self.tcp_addr = (ip, 9601)
        self.udp_addr = (ip, 9602)

        self.status_queue = []

    def set_id(self, worker_id):
        self.worker_id = worker_id
        self.streamer = stdout_stream.Sender(self.udp_addr, self.worker_id)

    async def init_connect(self):
        logger.info("Initializing with controller")
        try:
            return await async_client.send_message(self.loop, self.tcp_addr, -1, InitMessage("Connecting worker to controller", socket.gethostname(), "accepting-work"))
        except TimeoutError:
            self._exit("3 second connection timeout")
        except ConnectionRefusedError:
            self._exit("connection refused")

    async def request_work(self):
        logger.info("Requesting work from controller")
        try:
            return await async_client.send_message(self.loop, self.tcp_addr, self.worker_id, RequestMessage("Requesting Work", True))
        except TimeoutError:
            self._exit("3 second connection timeout")
        except ConnectionRefusedError:
            self._exit("connection refused")

    async def execute_work(self, work):
        self.command = work["command"]
        
        work_logger.info(f"Starting job: \"{self.command['cmd']}\"")
        logger.info(f"Starting job {self.command['job_id']}")
               
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
                if self.command["capture_output"]:
                    self.streamer.send(buf)
            work_logger.info(full_log.decode())

            if process.returncode == 0 or process.returncode is None: 
                work_logger.info(f"Job {self.command['job_id']} finished successfully")
                logger.info(f"Job {self.command['job_id']} finished successfully")
                await self._send_status("Job Finished", CommandStatus.FINISHED, True)
            else:
                work_logger.warning(f"Job {self.command['job_id']} finished with an error")
                logger.warning(f"Job {self.command['job_id']} finished with an error")
                await self._send_status("Job Failed", CommandStatus.FINISHED, False)
        except Exception as e:
            work_logger.warning(f"Job {self.command['job_id']} failed to start")
            logger.exception(e)
            await self._send_status("Job Failed", CommandStatus.FINISHED, False)

        await asyncio.sleep(20)
        if self.status_queue:
            logger.debug("Attempting to send message queue")
            try:
                await async_client.send_message(self.loop, self.tcp_addr, self.worker_id, PingMessage("ping?"), timeout=120)

                for item in self.status_queue:
                    await self._send_status(item[0], item[1], item[2])
            except TimeoutError as e:
                logger.critical("Exiting with messages in queue")
                for item in self.status_queue:
                    logger.warning(f"Queued message: {item[0]}")
                self._exit("120 second connection timeout")
            except ConnectionRefusedError:
                self._exit("connection refused")

    async def _send_status(self, message, status, success):
        try:
            await async_client.send_message(self.loop, self.tcp_addr, self.worker_id, StatusMessage(message, status, success, self.command["job_id"]))
        except Exception:
            self.status_queue.append([message, status, success])

    def _exit(self, reason):
        logger.error(f"Failed to connect to controller server ({reason})")
        sys.exit(1)

async def main(ip):
    worker = Worker(ip)

    response = await worker.init_connect()
    worker.set_id(response["init"]["worker_id"])

    while True:
        work = await worker.request_work()

        if work["type"] == MessageType.NO_COMMAND:
            if work["callback"]["come_back"]:
                logger.debug("No work found, waiting")
                await asyncio.sleep(work["callback"]["interval"] / 1000)
                continue

        await worker.execute_work(work)

if __name__ == "__main__":
    ip = os.getenv("CONTROLLER_IP")
    if not ip:
        args = sys.argv
        if len(args) != 2:
            print("Please provide an ip address to connect to")
            quit()
    
    # General logging
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter("[%(levelname)s]: %(message)s")
    console_handler.setFormatter(console_formatter)

    log_path = os.getenv("CLISTRIBUTE_LOGS", "cli-worker.log")
    file_handler = RotatingFileHandler(log_path, maxBytes = 5*1024*1024, backupCount = 1)
    file_handler.setLevel(logging.WARNING)
    file_formatter = logging.Formatter("%(asctime)s: [%(levelname)s]: %(message)s")
    file_handler.setFormatter(file_formatter)

    logger = logging.getLogger("worker")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    # STDOUT from CLI jobs
    work_log_path = os.getenv("WORK_LOGS", "work.log")
    work_handler = RotatingFileHandler(work_log_path, maxBytes = 5*1024*1024, backupCount = 2)
    work_handler.setLevel(logging.INFO)
    work_formatter = logging.Formatter("%(asctime)s: %(message)s")
    work_handler.setFormatter(work_formatter)

    work_logger = logging.getLogger("running-work")
    work_logger.setLevel(logging.INFO)
    work_logger.addHandler(work_handler)

    asyncio.run(main(ip))