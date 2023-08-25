import os
import sys
import shlex
import signal
import socket
import asyncio
import logging

import networking.async_client as async_client
import networking.stdout_stream as stdout_stream
from shared.message import InitMessageToController, RequestMessage, StatusMessage, PingMessage, ShutdownMessage
from shared.command import CommandStatus

logger = logging.getLogger("worker")
work_logger = logging.getLogger("running-work")

class Worker():
    def __init__(self, ip):
        self.loop = asyncio.get_running_loop()
        self.tcp_addr = (ip, int(os.getenv("TCP_PORT", 9601)))
        self.udp_addr = (ip, int(os.getenv("UDP_PORT", 9602)))
        logger.debug(f"TCP: {self.tcp_addr}")
        logger.debug(f"UDP: {self.udp_addr}")

        self.status_queue = []

        self.running = True
        self._working = False
        self.loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(self._handle_shutdown()))
        self.loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(self._handle_shutdown()))

    def set_id(self, worker_id):
        self.worker_id = worker_id
        self.streamer = stdout_stream.Sender(self.udp_addr, self.worker_id)

    async def init_connect(self):
        logger.info("Initializing with controller")
        try:
            return await async_client.send_message(self.loop, self.tcp_addr, -1, InitMessageToController("Connecting worker to controller", socket.gethostname(), "accepting-work"))
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

        self._working = True
        work_logger.info(f"Starting job {self.command['job_id']}: \"{self.command['cmd']}\"")
        logger.info(f"Starting job {self.command['job_id']}")

        try:
            cmd = shlex.split(self.command["cmd"])
            self.process = await asyncio.create_subprocess_exec(
                        *cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.STDOUT)

            await self._send_status("Running Job", CommandStatus.RUNNING, False)

            await self._capture_output()

            if self.process.returncode == 0 or self.process.returncode is None: 
                work_logger.info(f"Job {self.command['job_id']} finished successfully")
                logger.info(f"Job {self.command['job_id']} finished successfully")
                await self._send_status("Job Finished", CommandStatus.FINISHED, True)
            elif self.process.returncode == -15:
                # Job terminated, handled elsewhere
                return
            else:
                work_logger.warning(f"Job {self.command['job_id']} finished with an error")
                logger.warning(f"Job {self.command['job_id']} finished with an error")
                await self._send_status("Job Failed", CommandStatus.FINISHED, False)
        except Exception as e:
            work_logger.warning(f"Job {self.command['job_id']} failed to start")
            logger.exception(e)
            await self._send_status("Job Failed", CommandStatus.FINISHED, False)

        if self.status_queue:
            await self._dump_message_queue()

        self._working = False

    async def _send_status(self, message, status, success):
        try:
            await async_client.send_message(self.loop, self.tcp_addr, self.worker_id, StatusMessage(message, status, success, self.command["job_id"]))
        except Exception:
            self.status_queue.append([message, status, success])

    async def _capture_output(self):
        full_log = b""
        self.streamer.start()
        while self.process.returncode is None:
            buf = await self.process.stdout.read(20)
            if not buf:
                break
            full_log += buf
            if self.command["capture_output"]:
                self.streamer.send(buf)
        self.streamer.finish()
        work_logger.info(full_log.decode())

    async def _dump_message_queue(self):
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
            logger.critical("Exiting with messages in queue")
            for item in self.status_queue:
                logger.warning(f"Queued message: {item[0]}")
            self._exit("connection refused")

    def _exit(self, reason):
        logger.error(f"Failed to connect to controller server ({reason})")
        sys.exit(1)

    async def _handle_shutdown(self):
        logger.info("Recieved shutdown signal")
        self.running = False

        if self._working:
            logger.critical("Shutting down while working, terminating job")
            self.process.terminate()

            try:
                await async_client.send_message(self.loop, self.tcp_addr, self.worker_id, ShutdownMessage(False, self.command['job_id']))
            except:
                pass
        else:
            try:
                await async_client.send_message(self.loop, self.tcp_addr, self.worker_id, ShutdownMessage(True))
            except:
                pass
