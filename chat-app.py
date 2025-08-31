# gui_client.py
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog


class ChatGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chat Application")

        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD)
        self.chat_area.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)
        self.chat_area.config(state=tk.DISABLED)

        self.msg_entry = tk.Entry(self.root)
        self.msg_entry.pack(padx=20, pady=5, fill=tk.X)
        self.msg_entry.bind("<Return>", self.send_message)

        self.send_btn = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_btn.pack(padx=20, pady=5)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = simpledialog.askstring("Nickname", "Choose a nickname:", parent=self.root)

    def connect(self, host='localhost', port=12345):
        try:
            self.client_socket.connect((host, port))
            self.client_socket.send(self.nickname.encode('utf-8'))

            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()

        except Exception as e:
            self.display_message(f"Connection error: {e}")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    self.display_message(message)
            except:
                self.display_message("Disconnected from server")
                break

    def send_message(self, event=None):
        message = self.msg_entry.get()
        if message:
            try:
                self.client_socket.send(message.encode('utf-8'))
                self.msg_entry.delete(0, tk.END)
            except:
                self.display_message("Error sending message")

    def display_message(self, message):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, message + "\n")
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def run(self):
        self.connect()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        self.client_socket.close()
        self.root.destroy()


if __name__ == "__main__":
    app = ChatGUI()
    app.run()
