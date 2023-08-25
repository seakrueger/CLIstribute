import json
import queue
import logging
import threading

from flask import Flask, Response, send_from_directory, request

from shared.command import Command, CommandStatus
from database import CommandDatabase, WorkerDatabase
from networking.stdout_stream_endpoint import message_logs

logger = logging.getLogger("controller")

app = Flask(__name__)
flask_logger = logging.getLogger('werkzeug')
flask_logger.setLevel(logging.ERROR)

commands_db = CommandDatabase()
workers_db = WorkerDatabase()

@app.route("/")
def base():
    return send_from_directory('svelte-webapp/public', 'index.html')

@app.route("/<path:path>")
def home(path):
    return send_from_directory('svelte-webapp/public', path)

@app.route("/api/submit")
def submission():
    raw_data = request.args.get('data')
    data = json.loads(raw_data)

    command = Command(data["cmd"], CommandStatus.QUEUED, data["capture"])
    commands_db.add_command(command)

    response = json.dumps({
        "status": "okay"
    })
    return response

@app.route("/api/commands")
def get_commands():
    commands = commands_db.get_all_commands()
    
    commands_json = json.dumps([dict(command) for command in commands])
    
    return commands_json

@app.route("/api/workers")
def get_workers():
    workers = workers_db.get_all_workers()

    worker_json = json.dumps([dict(worker) for worker in workers])

    return worker_json

@app.route("/api/logs")
def get_stdout_streams():
    log_json = json.dumps(message_logs)

    return Response(log_json, content_type="application/json")

def start_webapp(shutdown_signal: threading.Event, finished_shutdown: queue.Queue, addr, config):
    finished_shutdown.put(threading.current_thread().name)

    logger.info(f"starting {threading.current_thread().name} on {addr}")
    app.run(host=addr[0], port=addr[1])

    logger.info(f"Finished {threading.current_thread().name} thread")
