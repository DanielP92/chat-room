import sys
import socket
import json
from threading import Thread
from playsound import playsound
import qt_elements as gui

IP = 'XX.XX.XX.XX'
PORT = 8085
ADDR = (IP, PORT)
MAX_BYTES = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(ADDR)


class UserClient:
    def __init__(self):
        self.connected = True
        self.username_window = gui.UsernameWindow()
        self.chat_window = gui.ChatWindow()

        self.chat_window.message.returnPressed.connect(self.send_msg)
        self.username_window.submit_button.clicked.connect(self.set_username)
        self.username_window.user_submission.returnPressed.connect(self.set_username)

        self.new_msgs = []
        self.online_users = []
        self.triggers = {'connect': self.connect_sound,
                         'disconnect': self.disconnect_sound,
                         'whisper': self.whisper_sound, }

    def set_username(self):
        username = self.username_window.user_submission.text()
        if username and username not in self.online_users and username.isalnum():
            setattr(self, 'client_username', username)
            sock.send(self.client_username.encode('utf-8'))
            self.username_window.hide()
            self.chat_window.show()

    def send_msg(self):
        # sends message in self.message_area to server; connected to returnPress on self.message_area; '!quit' breaks loop
        msg_text = self.chat_window.message.text()
        msg_dict = {'user': self.client_username, 'msg': msg_text}
        encoded_data = json.dumps(msg_dict).encode()

        if msg_text == ['!quit', '/q']:
            sock.send(encoded_data)
            self.connected = False
            sys.exit()
        else:
            sock.send(encoded_data)

        self.chat_window.message.clear()

    def connect_sound(self):
        playsound('user_online.wav', block=False)

    def disconnect_sound(self):
        playsound('user_offline.wav', block=False)

    def whisper_sound(self):
        if not self.chat_window.isActiveWindow():
            playsound('whisper.wav', block=False)

    def recv_msg(self):
        # receives data sent by the server; checks for message, updates [self.online_users], then updates [self.new_msgs] (as appropriate)
        while self.connected:
            try:
                data = sock.recv(MAX_BYTES).decode('utf-8')
                msg_dict = json.loads(data)
                display_msg = ''

                if msg_dict['msg']:
                    for online_user in [x for x in msg_dict['active_users'] if x not in self.online_users]:
                        self.online_users.append(online_user)
                    for offline_user in [x for x in self.online_users if x not in msg_dict['active_users']]:
                        self.online_users.remove(offline_user)

                    if msg_dict['username']:
                        display_msg = f"{msg_dict['username']}: {msg_dict['msg']}"
                    else:
                        display_msg = msg_dict['msg'].lstrip()

                    if 'SYSMSG' not in display_msg:
                        self.new_msgs.append(display_msg)

                    if msg_dict['trigger']:
                        triggered_function = self.triggers[msg_dict['trigger']]
                        triggered_function()

                    print(f"{msg_dict['username']} {msg_dict['msg']}", self.online_users)

            except Exception as e:
                print(f'CLIENT - ERROR GETTING MESSAGES: {e}')
                break

    def display_users(self):
        self.chat_window.user_display.setPlainText("\n".join(self.online_users))

    def display_msgs(self):
        while self.new_msgs:
            self.chat_window.chat_display.appendPlainText(self.new_msgs.pop(0))


def start_client():
    u = UserClient()

    chat_timer, user_timer = gui.QTimer(), gui.QTimer()
    chat_timer.timeout.connect(u.display_msgs)
    user_timer.timeout.connect(u.display_users)
    chat_timer.start(500)
    user_timer.start(2000)

    recv_thread = Thread(target=u.recv_msg)
    recv_thread.start()

    sys.exit(gui.app.exec_())


if __name__ == '__main__':
    with sock:
        start_client()
