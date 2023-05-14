import socket



i = 0
while i < 100:
    try:
        with socket.create_connection(('localhost', 9090)) as sock:
            sock.send('hello, world!'.encode())

            data = sock.recv(1024)

            sock.close()

            print(data.decode())
        i += 1
    except ConnectionError:
        continue