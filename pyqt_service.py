import ast
import sys
import socket
import threading
from queue import Queue
from PyQt5 import QtWidgets, QtGui, QtCore


class LeftWidget(QtWidgets.QWidget):
    def __init__(self, right_widget):
        super().__init__()

        self.right_widget = right_widget

        # 图片
        image_label = QtWidgets.QLabel()
        image = QtGui.QPixmap("resource/img/logo.png")
        image = image.scaled(100, 75, QtCore.Qt.AspectRatioMode.KeepAspectRatio)  # 调整图片大小以适应标签
        image_label.setPixmap(image)
        image_label.setAlignment(QtCore.Qt.AlignCenter)

        # 创建一个水平布局并在其中添加图片标签
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(image_label)

        # 创建一个垂直布局来包含水平布局，并在左侧窗口中使用该布局
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addLayout(layout)
        left_layout.addStretch(1)  # 添加弹簧，使图片居中显示

        # 加粗文字
        bold_label = QtWidgets.QLabel("薇薇聊天室")
        bold_font = QtGui.QFont()
        bold_font.setBold(True)
        bold_font.setPointSize(16)
        bold_label.setFont(bold_font)
        bold_label.setAlignment(QtCore.Qt.AlignCenter)

        # 输入框
        self.ip_label = QtWidgets.QLabel("IP:")
        self.ip_line_edit = QtWidgets.QLineEdit()

        self.host_label = QtWidgets.QLabel("Host:")
        self.host_line_edit = QtWidgets.QLineEdit()

        # 创建一个容器小部件
        button_container = QtWidgets.QWidget()

        # 创建一个水平布局，并将容器小部件设置为该布局的父级
        button_layout = QtWidgets.QHBoxLayout(button_container)

        # 确认按钮
        self.confirm_button = QtWidgets.QPushButton("确认")
        self.confirm_button.setFixedWidth(130)
        self.confirm_button.clicked.connect(self.confirm)

        # 将确认按钮添加到水平布局中
        button_layout.addWidget(self.confirm_button)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(image_label)
        layout.addWidget(bold_label)
        layout.addWidget(self.ip_label)
        layout.addWidget(self.ip_line_edit)
        layout.addWidget(self.host_label)
        layout.addWidget(self.host_line_edit)
        layout.addWidget(button_container)
        layout.addStretch()  # 添加弹簧，使内容居中显示
        self.setLayout(layout)

    def confirm(self):
        ip = self.ip_line_edit.text()
        host = self.host_line_edit.text()

        # 保存IP和Host为全局变量或类的属性
        global ip_address
        global host_name
        ip_address = ip
        host_name = host

        # 创建并显示对话框
        reply = QtWidgets.QMessageBox.question(self, "提示", f"ip:{ip_address}\nhost:{host_name}",
                                               QtWidgets.QMessageBox.Yes)
        if reply == QtWidgets.QMessageBox.Yes:
            # 用户点击了确认按钮
            right_widget = self.parent().right_widget
            right_widget.clear_text()
            # 创建线程来启动服务器
            server_thread = threading.Thread(target=right_widget.start_server)
            server_thread.start()


class ClientThread(threading.Thread):
    def __init__(self, client_socket, address, parent):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.address = address
        self.parent = parent

    def run(self):
        self.parent.log_message(f"接收来自 {self.address[0]}:{self.address[1]} 的连接")

        while True:
            data = self.client_socket.recv(1024)
            if not data:
                break
            message = data.decode("utf-8")
            message_dict = ast.literal_eval(message)
            print(message_dict)
            self.parent.log_message(message_dict["username"]+":"+message_dict["message"])
        self.client_socket.close()


class RightWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

        self.thread_pool = ThreadPool()

    def start_server(self):
        self.log_message("服务端启动...")

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip_address, int(host_name)))
        server_socket.listen(5)

        while True:
            client_socket, address = server_socket.accept()
            client_thread = ClientThread(client_socket, address, self)
            self.thread_pool.add_task(client_thread.run)

    def log_message(self, message):
        self.text_edit.append(message)
        scrollbar = self.text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_text(self):
        self.text_edit.clear()


class ThreadPool:
    def __init__(self, num_threads=5):
        self.task_queue = Queue()
        self.threads = []

        for _ in range(num_threads):
            thread = threading.Thread(target=self.worker)
            thread.start()
            self.threads.append(thread)

    def add_task(self, task):
        self.task_queue.put(task)

    def worker(self):
        while True:
            task = self.task_queue.get()
            task()
            self.task_queue.task_done()


class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("WeiChat服务端")
        self.setFixedSize(600, 400)

        icon = QtGui.QIcon("resource/img/logo.png")
        self.setWindowIcon(icon)

        self.right_widget = RightWidget()
        self.left_widget = LeftWidget(self.right_widget)

        main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(main_layout)

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self.left_widget)
        main_layout.addLayout(left_layout, stretch=4)

        right_layout = QtWidgets.QVBoxLayout()
        right_layout.addWidget(self.right_widget)
        main_layout.addLayout(right_layout, stretch=7)


if __name__ == "__main__":
    ip_address = ""
    host_name = ""
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())