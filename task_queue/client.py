from socket import *


def client(message):
    data = message
    if not data:
        tcp_socket.close()
    data = str.encode(data)
    tcp_socket.send(data)
    data = tcp_socket.recv(1024)
    print(data)


if __name__ == '__main__':
    # for file in os.listdir():
    #     if file.startswith('last_state'):
    #         os.remove(file)
    host = '127.0.0.1'
    port = 8080
    addr = (host, port)
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    tcp_socket.connect(addr)
    client('ADD test_queue 20 808080')
    client('ADD test_queue 30 909090')
    tcp_socket.close()
