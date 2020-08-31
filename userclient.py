class Person:
    def __init__(self, socket, addr, username):
        self.socket = socket
        self.addr = addr
        self.username = username
        self.blocked_users = []

    def __str__(self):
        return self.username + self.addr
