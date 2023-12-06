import os
import sys
import time
import logging
import argparse
from logging.handlers import RotatingFileHandler

from controller import ControllerApp

def main(args):
    controller = ControllerApp(args)

    controller.start()
    while not controller.shutdown:
        controller.run()
        time.sleep(1)
    
    logger.info(f"Shutdown in {(time.time() - controller.shutdown_time):.2f} seconds")

    if args.silent:
        print("\nShut down successfully")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        prog="Controller (CLIstribute)",
                        description="Controller for distribute computing of command line jobs")
    parser.add_argument("-v", "--verbose", action='store_true', help="Enable additional logging", required=False)
    parser.add_argument("-s", "--silent", action='store_true', help="Disable logging to console", required=False)
    parser.add_argument("--webapp", action='store_true', help="Run %(prog)s with a webapp", required=False)

    args = parser.parse_args()

    logger = logging.getLogger("controller")
    logger.setLevel(logging.DEBUG)

    if not args.silent:
        console_handler = logging.StreamHandler(sys.stdout)
        if args.verbose or int(os.getenv("LOG_DEBUG") or 0) == 1:
            console_handler.setLevel(logging.DEBUG)
        else:
            console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("[%(levelname)s]: %(threadName)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(console_handler)

    log_path = os.getenv("CLISTRIBUTE_LOGS", "cli-controller.log")
    file_handler = RotatingFileHandler(log_path, maxBytes = 5*1024*1024, backupCount = 2)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter("%(asctime)s: [%(levelname)s]: %(threadName)s - %(message)s")
    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)

    main(args)
