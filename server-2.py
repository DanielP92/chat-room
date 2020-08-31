import socket
import json
from threading import Thread
from userclient import Person

IP = '192.168.0.5'
PORT = 8085
ADDR = (IP, PORT)
MAX_BYTES = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(ADDR)
live = True
sock.listen(10)

persons = {}
sockets = []
usernames = []


print(f'SERVER IS ONLINE: {sock}')


def broadcast(client, msg, trigger=None):
    # sends current users and user message to all clients in [sockets]; if message can't be sent to client, exception is thrown and client removed from [sockets]
    usernames = [x.username for x in persons.values()]

    msg_dict = {'username': client, 'msg': msg, 'active_users': usernames, 'trigger': trigger}

    for person in persons.values():
        try:
            if not msg_dict['username']:
                encoded_data = json.dumps(msg_dict).encode()
                person.socket.send(encoded_data)

            elif person.socket not in [x.socket for x in persons[client].blocked_users]:
                msg_dict['active_users'] = [x for x in usernames if x not in [x.username for x in persons[client].blocked_users]]
                encoded_data = json.dumps(msg_dict).encode()
                person.socket.send(encoded_data)

        except Exception as e:
            print(f'SERVER - ERROR SENDING MESSAGE TO CLIENT. RETURNED EXCEPTION WAS:\n{e}\nREFRESHING CONNECTIONS...')
            sockets = [x.socket for x in persons.values()]
            usernames = [x.username for x in persons.values()]


def disconnect_client(person):
    disconnect_string = f'{person.username} has disconnected!'
    broadcast("", disconnect_string, trigger='disconnect')
    print(f'{person.socket} has DISCONNECTED')


def refresh_connections():
    print('Refreshing client connections...')
    broadcast("", 'SYSMSG - Refreshing connections...')
    sockets = [x.socket for x in persons.values()]
    usernames = [x.username for x in persons.values()]
    print(f'Active connections: {len(sockets)}')
    print(f'users in chat: {usernames}')


def check_for_command(msg):
    if len(msg) >= 2 and msg[1]:
        command = str(msg[1])
        if command in list(chat_commands.keys()):
            try:
                return chat_commands[command]
            except Exception as e:
                print(f'SERVER - ERROR RETRIEVING COMMAND. RETURNED EXCEPTION WAS:\n{e}')
        else:
            return False
    else:
        return False


def client_communication(person):
    # announce to server that person has joined
    join_string = f'{person.username} has joined the chat!'
    broadcast("", join_string, trigger='connect')

    # main chat loop; receives messages from client and broadcasts to all other clients in [sockets]; '!quit' breaks loop; closing window throws exception and breaks loop
    while True:
        try:
            data = person.socket.recv(MAX_BYTES).decode('utf-8')
            msg_dict = json.loads(data)

            if msg_dict['msg'] in ['!quit', '/q']:
                disconnect_client(person)
                persons.pop(person.username, None)
                refresh_connections()
                break

            msg_li = [msg_dict['user']] + msg_dict['msg'].split(" ")
            command_used = check_for_command(msg_li)

            if command_used:
                command_used(msg_li, person)

            elif msg_dict['msg']:
                broadcast(msg_dict['user'], msg_dict['msg'])
                print(f"user: {msg_dict['user']}", f"msg: {msg_dict['msg']}")

        except Exception as e:
            print(f'SERVER - ISSUE WITH CLIENT CONNECTION. RETURNED EXCEPTION WAS:\n{e}\nCLOSING CONNECTION...')
            disconnect_client(person)
            persons.pop(person.username, None)
            refresh_connections()
            break


# Chat commands
def whisper(msg, sender):
    # triggered when client uses /w <username>
    target = persons[msg[2]]
    whisper = " ".join(msg[3:])

    msg_dict = {'username': "", 'msg': "", 'active_users': usernames, 'trigger': None}
    to_sender = f'whisper to {target.username}: {whisper}'
    to_target = f'whisper from {sender.username}: {whisper}'

    msg_dict['msg'] = to_sender
    sender.socket.send(json.dumps(msg_dict).encode())

    msg_dict['msg'] = to_target
    msg_dict['trigger'] = 'whisper'
    target.socket.send(json.dumps(msg_dict).encode())

    print(f'whisper from {sender.username} to {target.username}: {whisper}')


def block_user(msg, person):
    target = persons[msg[2]]
    person.blocked_users.append(target)
    target.blocked_users.append(person)
    msg_dict = {'username': "", 'msg': f"{target.username} has now been blocked", 'active_users': usernames, 'trigger': None}
    person.socket.send(json.dumps(msg_dict).encode())
    print(f'{person.username} has blocked {target.username}')


def unblock_user(msg, person):
    target = persons[msg[2]]
    person.blocked_users.remove(target)
    target.blocked_users.remove(person)
    msg_dict = {'username': "", 'msg': f"{target.username} has now been unblocked", 'active_users': usernames, 'trigger': None}
    person.socket.send(json.dumps(msg_dict).encode())
    print(f'{person.username} has unblocked {target.username}')


def self_command(msg, person):
    # triggered when client uses /me
    msg.remove(msg[1])
    self_msg = " ".join(msg)
    broadcast("", self_msg)


chat_commands = {'/b': block_user,
                 '/me': self_command,
                 '/ub': unblock_user,
                 '/w': whisper, }


while live:
    try:
        c_socket, addr = sock.accept()
        username = c_socket.recv(MAX_BYTES).decode('utf-8')
        person = Person(c_socket, addr, username)

        persons[username] = person
        sockets = [x.socket for x in persons.values()]
        usernames = [x.username for x in persons.values()]

        client_thread = Thread(target=client_communication, args=(person,))
        client_thread.start()

        print(f'SERVER - NEW CLIENT @ {addr}')
        print(f'Active connections: {len(sockets)}')

    except Exception as e:
        print(f'SERVER - ERROR ACCEPTING CONNECTIONS. RETRUNED EXCEPTION WAS:\n{e}\nCLOSING SERVER...')
        sock.close()
        live = False
