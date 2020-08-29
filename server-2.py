import socket
import json
import re
import time
from threading import Thread
from userclient import Person

IP = 'XX.XX.XX.XX'
PORT = 8085
ADDR = (IP, PORT)
MAX_BYTES = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(ADDR)
live = True
sock.listen(10)

persons = []
sockets = []
usernames = []


print(f'SERVER IS ONLINE: {sock}')


def broadcast(msg, person):
    # sends current users and user message to all clients in [sockets]; if message can't be sent to client, exception is thrown and client removed from [sockets]
    sockets = [x.socket for x in persons]

    for s in sockets:
        try:
            to_client(s, msg)
        except Exception as e:
            print(f'SERVER - ERROR SENDING MESSAGE TO CLIENT {s}:\n {e}. REFRESHING CONNECTIONS...')
            sockets = [x.socket for x in persons]
            usernames = [x.username for x in persons]
            print(f'Active connections: {len(sockets)}')


def disconnect_client(person):
    disconnect_string = f'{person.username} has disconnected!'.encode('utf-8')
    broadcast(disconnect_string, person)

    sockets = [x.socket for x in persons]
    usernames = [x.username for x in persons]

    print(f'{person.socket} has DISCONNECTED')
    print(f'Active connections: {len(sockets)}')
    print(f'users in chat: {usernames}')


def check_for_command(msg, person):
    if len(msg) >= 2 and msg[1]:
        if str(msg[1]) in list(chat_commands.keys()):
            try:
                command = str(msg[1])
                command_function = chat_commands[command]
                return command_function
            except Exception as e:
                print(f'SERVER - NO SUCH COMMAND: {e}')
        else:
            return None
    else:
        return None


def client_communication(person):
    # announce to server that person has joined
    join_string = f'{person.username} has joined the chat!'.encode('utf-8')
    broadcast(join_string, person)

    # main chat loop; receives messages from client and broadcasts to all other clients in [sockets]; '!quit' breaks loop; closing window throws exception and breaks loop
    while True:

        try:
            msg = person.socket.recv(MAX_BYTES)

            if msg in [bytes('!quit', 'utf-8'), bytes('/q', 'utf-8')]:
                disconnect_client(person)
                break

            msg_li = msg.decode().split(" ")
            command_used = check_for_command(msg_li, person)

            if command_used:
                command_used(msg_li, person)

            elif msg:
                broadcast(msg, person)
                print(msg.decode())

        except ConnectionResetError as e:
            print(f'SERVER - CONNECTION RESET BY CLIENT {person.socket}. CLOSING CONNECTION...')
            persons.remove(person)
            disconnect_client(person)
            break


def to_client(sock, msg):
    usernames = [x.username for x in persons]
    encoded_users = json.dumps(usernames).encode()
    sock.send(encoded_users)
    time.sleep(0.1)
    sock.send(msg)


def whisper(msg, person):
    target_user = msg[2]

    if target_user in [x for x in usernames if x != person.username]:
        for p in [x for x in persons if x.username == target_user]:
            whisper = " ".join(msg[3:])
            a_msg = f'whisper to {p.username}: {whisper}'
            b_msg = f'whisper from {person.username}: {whisper}'

            to_client(person.socket, a_msg.encode('utf-8'))
            to_client(p.socket, b_msg.encode('utf-8'))

            print(f'whisper from {person.username} to {p.username}: {whisper}')


def self_command(msg, person):
    msg.remove(msg[1])
    new_msg = " ".join(msg)
    new_msg = re.sub("[:]", "", new_msg)

    broadcast(new_msg.encode('utf-8'), person)


chat_commands = {'/w': whisper,
                 '/me': self_command, }


while live:
    try:
        c_socket, addr = sock.accept()
        username = c_socket.recv(MAX_BYTES).decode('utf-8')
        person = Person(c_socket, addr, username)
        persons.append(person)

        sockets = [x.socket for x in persons]
        usernames = [x.username for x in persons]
        encoded_users = json.dumps(usernames).encode()

        client_thread = Thread(target=client_communication, args=(person,))
        client_thread.start()

        print(f'SERVER - NEW CLIENT @ {addr}')
        print(f'Active connections: {len(sockets)}')

    except Exception as e:
        print(f'SERVER - ERROR ACCEPTING CONNECTIONS: {e}')
        sock.close()
        live = False
