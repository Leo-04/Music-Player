import os
import socket
import sys
from threading import Thread
import hashlib


class Single:
    """
    Uses sockets to implement a single application instance
    """

    socket: socket.socket
    can_bind: bool = False
    thread: Thread | None = None
    callback: callable = None

    @staticmethod
    def generate_port(file_id: str) -> int:
        """Allows multiple apps using this code to have different ports"""

        return 50000 + (int(hashlib.md5(file_id.encode("UTF-8")).hexdigest(), 16) % 15000)

    def __init__(self, port: int, callback: callable = lambda args: print(args)):
        self.callback = callback
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind(('127.0.0.1', port))
            self.socket.listen(1)
            self.can_bind = True
            print("Listen on port:", port)
        except Exception as err:
            self.socket.connect(('127.0.0.1', port))
            self.can_bind = False
            print("Sending on port:", port, "\nError:", err)

    def send_argv(self, argv: list[str]):
        """Sends the argv for a second instance to the main instance"""

        byte_array = len(argv).to_bytes(4, "big", signed=False)
        for arg in argv:
            byte_array += len(arg).to_bytes(4, "big", signed=False)
            byte_array += arg.encode("UTF-8")

        self.socket.send(byte_array)

    def thread_loop(self):
        """Loops in a thread"""

        self.thread = Thread(target=self.loop)
        self.thread.start()

    def loop(self):
        """Run the socket server for the main instance"""

        while self.can_bind:
            try:
                connection, address = self.socket.accept()
            except Exception:
                break  # socket was destroyed

            length = int.from_bytes(connection.recv(4), "big", signed=False)
            argv = []
            for i in range(length):
                length = int.from_bytes(connection.recv(4), "big", signed=False)
                argv.append(connection.recv(length).decode("UTF-8"))

            connection.close()

            self.callback(argv)

    def is_not_main(self) -> bool:
        """Checks if this instance is not the main one"""

        return not self.can_bind

    def close(self):
        """Closes the socket"""

        self.can_bind = False
        self.socket.close()
    
    def join():
        """if the loop is threaded, join it"""
    
        if self.thread is not None:
            self.thread.join()
            self.thread = None
