import socket

class Sender():
    def __init__(self, addr, worker_id):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.addr = addr
        self.worker_id = bytes(str(worker_id).rjust(3, "0").encode())

    def send(self, output):
        app_output = output + self.worker_id
        self.sock.sendto(app_output, self.addr)

    def start(self):
        self.send("<<SOM>>".encode())

    def finish(self):
        self.send("<<EOM>>".encode())