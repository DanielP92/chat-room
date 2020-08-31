from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

app = QApplication([])


class UsernameWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Choose a Username")
        self.setGeometry(200, 200, 300, 100)

        outer_layout = QVBoxLayout()
        inner_layout_username = QVBoxLayout()
        inner_layout_buttons = QHBoxLayout()

        outer_layout.setContentsMargins(20, 20, 20, 20)
        outer_layout.setSpacing(5)
        label = QLabel('Enter your username:', self)
        self.user_submission = QLineEdit(self)
        inner_layout_username.addWidget(label)
        inner_layout_username.addWidget(self.user_submission)

        self.submit_button = QPushButton('Submit', self)
        cancel_button = QPushButton('Cancel', self)
        inner_layout_buttons.addWidget(self.submit_button)
        inner_layout_buttons.addWidget(cancel_button)

        outer_layout.addLayout(inner_layout_username)
        outer_layout.addLayout(inner_layout_buttons)

        self.setLayout(outer_layout)
        cancel_button.clicked.connect(self.close)

        self.show()


class ChatWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Daniel's Chat Room")
        self.setGeometry(200, 200, 650, 650)

        window = QWidget(self)

        outer_layout = QHBoxLayout()
        inner_layout_chat = QVBoxLayout()
        message_bar = QHBoxLayout()
        inner_layout_usernames = QVBoxLayout()
        inner_layouts = [inner_layout_chat, inner_layout_usernames]

        outer_layout.setContentsMargins(20, 5, 20, 20)
        outer_layout.setSpacing(5)

        self.send_button = QPushButton('Send')
        self.message = QLineEdit(window)
        message_bar.addWidget(self.send_button)
        message_bar.addWidget(self.message)

        chat_label = QLabel('Chat:', window)
        self.chat_display = QPlainTextEdit(window)
        self.chat_display.setMinimumWidth(400)

        chat_widgets = [chat_label, self.chat_display]
        for w in chat_widgets:
            inner_layout_chat.addWidget(w)

        inner_layout_chat.addLayout(message_bar)

        user_label = QLabel('Users:', window)
        self.user_display = QPlainTextEdit(window)
        self.user_display.setFixedWidth(200)

        user_widgets = [user_label, self.user_display]
        for w in user_widgets:
            inner_layout_usernames.addWidget(w)

        self.chat_display.setFocusPolicy(Qt.NoFocus)
        self.user_display.setFocusPolicy(Qt.NoFocus)

        for layout in inner_layouts:
            outer_layout.addLayout(layout)

        window.setLayout(outer_layout)
        self.setCentralWidget(window)
