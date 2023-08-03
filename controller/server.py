import queue
import logging
import threading

from flask import Flask, send_from_directory
import random

logger = logging.getLogger("controller")
app = Flask(__name__)

# Path for our main Svelte page
@app.route("/")
def base():
    return send_from_directory('ui/svelte-webapp/public', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('ui/svelte-webapp/public', path)

@app.route("/rand")
def hello():
    return str(random.randint(0, 100))

def start_webapp(shutdown_signal: threading.Event, finished_shutdown: queue.Queue, addr):
    finished_shutdown.put(threading.current_thread().name)

    logger.info(f"starting {threading.current_thread().name} on {addr}")
    app.run(port=addr[1])

    logger.info(f"Finished {threading.current_thread().name} thread")
