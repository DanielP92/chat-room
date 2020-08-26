import sys
import socket
import json
from threading import Thread
import qt_elements as gui

IP = 'XX.XX.XX.XX'
PORT = 8085
ADDR = (IP, PORT)
MAX_BTYES = 1024

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

    def set_username(self):
        username = self.username_window.user_submission.text()
        if username:
            setattr(self, 'client_username', username)
            sock.send(self.client_username.encode('utf-8'))
            self.username_window.hide()
            self.chat_window.show()

    def get_users(self):
        # receives online users from server and updates [self.online_users], removes users who have disconnected
        try:
            all_users = eval(sock.recv(MAX_BTYES).decode())
            if all_users:
                for user in [x for x in all_users if x not in self.online_users]:
                    self.online_users.append(user)
                for offline_user in [x for x in self.online_users if x not in all_users]:
                    self.online_users.remove(offline_user)

        except Exception as e:
            print(f'CLIENT - ERROR GETTING USERS: {e}')
            self.connected = False
            sys.exit()

    def get_message(self):
        # receives message from server
        msg = sock.recv(MAX_BTYES).decode('utf-8')

        if msg:
            print(msg, self.online_users)
            self.new_msgs.append(msg)

    def send_msg(self):
        # sends message in self.message_area to server; connected to returnPress on self.message_area; '!quit' breaks loop
        msg = self.chat_window.message.text()

        if msg == '!quit':
            sock.send(msg.encode('utf-8'))
            self.connected = False
            sys.exit()
        else:
            sock.send(f'{self.client_username}: {msg}'.encode('utf-8'))

        self.chat_window.message.clear()

    def recv_msg(self):
        # the server sends current users and message; function receives both and translates into data to facilitate gui update
        while self.connected:
            try:
                self.get_users()
                self.get_message()
            except Exception as e:
                print(f'CLIENT - ERROR GETTING MESSAGES: {e}')
                self.connected = False
                sys.exit()

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
    chat_timer.start(100)
    user_timer.start(1000)

    recv_thread = Thread(target=u.recv_msg)
    recv_thread.start()

    sys.exit(gui.app.exec_())


if __name__ == '__main__':
    with sock:
        start_client()
