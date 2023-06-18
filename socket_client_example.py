import socket
import json


data_dict = {
    "action": {"steeting": -1.06},
    "observation": [1,2,3,4,5]
}

data_json = json.dumps(data_dict).encode("utf-8")
print("Request size is: ", len(data_json))

with socket.create_connection(('localhost', 9090)) as sock:
    sock.sendall(data_json)
    while True:
        chunks = b''
        chunk = sock.recv(4096)
        if not chunk:
            break
        chunks += chunk
        print("Response size is: ", len(chunks.decode("utf-8")))
        print("Response size is: ", json.loads(chunks.decode("utf-8")))


        # try:
        #     size = sock.recv(8)
        #     print("response size is: ", int.from_bytes(size, byteorder="little"))
        #     data = sock.recv(4096)
        #     print(int.from_bytes(data, byteorder="little"))
        #     break
        # except ConnectionResetError:
        #     pass


# i = 0
# while i < 100:
#     try:
#         with socket.create_connection(('localhost', 9090)) as sock:
#             sock.send('hello, world!'.encode())

#             data = sock.recv(1024)

#             sock.close()

#             print(data.decode())
#         i += 1
#     except ConnectionError:
#         continue