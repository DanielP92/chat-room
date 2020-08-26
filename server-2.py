import socket
import json
from threading import Thread

IP = 'XX.XX.XX.XX'
PORT = 8085
ADDR = (IP, PORT)
MAX_BTYES = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(ADDR)
live = True
sock.listen(10)

sockets = []
usernames = []

print(f'SERVER IS ONLINE: {sock}')


def broadcast(msg, username):
    # sends current users and user message to all clients in [sockets]; if message can't be sent to client, exception is thrown and client removed from [sockets]
    for s in sockets:
        try:
            s.send(json.dumps(usernames).encode())
            s.send(msg)
            print(f'users in chat: {usernames}')
        except Exception as e:
            print(f'SERVER - ERROR SENDING MESSAGE TO CLIENT {s}:\n {e}. REMOVING SOCKET FROM CONNECTIONS.')
            sockets.remove(s)
            usernames.remove(username)
            print(f'Active connections: {len(sockets)}')


def client_communication(client):
    # receive username from client and add to current users; tell all clients this user has joined
    username = client.recv(MAX_BTYES).decode('utf-8')
    usernames.append(username)
    usernames.sort()
    msg = f'{username} has joined the server!'.encode('utf-8')
    broadcast(msg, username)

    # main chat loop; receives messages from client and broadcasts to all other clients in [sockets]; '!quit' breaks loop; closing window throws exception and breaks loop
    while True:
        try:
            msg = client.recv(MAX_BTYES)

            if msg == bytes('!quit', 'utf-8'):
                disconnect_string = f'{username} has disconnected!'.encode('utf-8')

                if usernames:
                    broadcast(disconnect_string, username)

                sockets.remove(client)
                usernames.remove(username)

                print(f'{client} has DISCONNECTED')
                print(f'Active connections: {len(sockets)}')
                print(f'users in chat: {usernames}')
                break

            elif msg:
                broadcast(msg, username)
                print(msg.decode())

        except ConnectionResetError as e:
            print(f'SERVER - CONNECTION RESET BY CLIENT {client}. CLOSING CONNECTION...')
            sockets.remove(client)
            usernames.remove(username)
            break


while live:
    try:
        c_socket, addr = sock.accept()
        sockets.append(c_socket)

        client_thread = Thread(target=client_communication, args=(c_socket,))
        client_thread.start()

        print(f'SERVER - NEW CLIENT @ {addr}')
        print(f'Active connections: {len(sockets)}')

    except Exception as e:
        print(f'SERVER - ERROR ACCEPTING CONNECTIONS: {e}')
        sock.close()
        live = False
