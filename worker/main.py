import os
import sys
import asyncio
import logging
from logging.handlers import RotatingFileHandler

import package_installer
from shared.message import MessageType
from worker import Worker

async def main(ip):
    worker = Worker(ip)

    init_response = await worker.init_connect()
    worker.set_id(init_response["init"]["worker_id"])

    if os.getenv("CLISTRIBUTE_APT"):
        package_installer.packages(init_response["init"]["packages"])

    while worker.running:
        work = await worker.request_work()

        if work["type"] == MessageType.NO_COMMAND:
            if work["callback"]["come_back"]:
                logger.debug("No work found, waiting")
                await asyncio.sleep(work["callback"]["interval"])
                continue
            else:
                logger.info("No more work required, stopping")
                sys.exit(0)
        elif work["type"] == MessageType.SHUTDOWN:
            logger.warning("Recieved shutdown signal from controller")
            sys.exit(0)

        await worker.execute_work(work)

if __name__ == "__main__":
    ip = os.getenv("CONTROLLER_IP")
    if not ip:
        args = sys.argv
        if len(args) != 2:
            print("Please provide an ip address to connect to")
            quit()
        ip = args[1]

    # General logging
    console_handler = logging.StreamHandler(sys.stdout)
    debug_level = os.getenv("LOG_DEBUG", 0)
    if int(debug_level) == 1:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("[%(levelname)s]: %(message)s")
    console_handler.setFormatter(console_formatter)

    log_path = os.getenv("CLISTRIBUTE_LOGS", "cli-worker.log")
    file_handler = RotatingFileHandler(log_path, maxBytes = 5*1024*1024, backupCount = 1)
    file_handler.setLevel(logging.INFO)
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