import socket
from PyQt5 import QtWidgets


class Client(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Client")

        self.ip_input = QtWidgets.QLineEdit()
        self.port_input = QtWidgets.QLineEdit()
        self.message_input = QtWidgets.QLineEdit()
        self.send_button = QtWidgets.QPushButton("Send")
        self.label = QtWidgets.QLabel("Response will be shown here.")

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(QtWidgets.QLabel("IP Address:"))
        self.layout.addWidget(self.ip_input)
        self.layout.addWidget(QtWidgets.QLabel("Port:"))
        self.layout.addWidget(self.port_input)
        self.layout.addWidget(QtWidgets.QLabel("Message:"))
        self.layout.addWidget(self.message_input)
        self.layout.addWidget(self.send_button)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.send_button.clicked.connect(self.send_message)

    def send_message(self):
        ip = self.ip_input.text()
        port = int(self.port_input.text())
        message = self.message_input.text()

        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect((ip, port))

        sk.send(message.encode("utf-8"))
        data = sk.recv(1024)
        response = data.decode("utf-8")
        self.label.setText(f"Response: {response}")

        sk.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    client = Client()
    client.show()
    app.exec_()