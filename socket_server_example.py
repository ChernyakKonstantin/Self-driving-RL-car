import socket
from enum import IntEnum
from random import randint
class Action(IntEnum):
    FORWARD = 1
    BACKWARD = 2
    LEFT = 3
    RIGHT = 4

class Request(IntEnum):
    ACTION = 1
    GREETING = 2

sock = socket.create_server(("localhost", 9090))

sock.listen(1)

while True:
    conn, addr = sock.accept()


    while True:
        data = conn.recv(4)
        if not data:
            break
        data = int.from_bytes(data, "little")
        if data == Request.ACTION:
            conn.send(randint(1,4).to_bytes(4, "little"))

    conn.close()