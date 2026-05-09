"""GUI startup screen and chat screen."""

import tkinter as tk
from tkinter import scrolledtext


class ChatGUI:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Secure Chat - CS 4173")
        self.root.geometry("640x480")

        # We swap the startup screen and the chat screen in and out of this frame.
        self.container = tk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Chat screen widgets (filled in by show_chat_screen).
        self.chat_display = None
        self.input_entry = None
        self.status_var = None
        self.send_handler = None

        # Startup screen widgets (filled in by show_startup_screen).
        self.password_var = None
        self.mode_var = None
        self.host_var = None
        self.port_var = None
        self.host_label = None
        self.host_entry = None
        self.error_var = None

    def show_startup_screen(self, on_start):
        self._clear_container()

        frame = tk.Frame(self.container, padx=24, pady=24)
        frame.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(frame, text="Secure Chat", font=("TkDefaultFont", 18, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 16))

        # Password (masked).
        tk.Label(frame, text="Password:").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=4)
        self.password_var = tk.StringVar()
        password_entry = tk.Entry(frame, textvariable=self.password_var, show="*", width=28)
        password_entry.grid(row=1, column=1, sticky="w", pady=4)

        # Mode: Host or Connect.
        tk.Label(frame, text="Mode:").grid(row=2, column=0, sticky="e", padx=(0, 8), pady=4)
        self.mode_var = tk.StringVar(value="Host")
        mode_frame = tk.Frame(frame)
        mode_frame.grid(row=2, column=1, sticky="w", pady=4)
        tk.Radiobutton(mode_frame, text="Host", variable=self.mode_var, value="Host",
                       command=self._on_mode_change).pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="Connect", variable=self.mode_var, value="Connect",
                       command=self._on_mode_change).pack(side=tk.LEFT, padx=(8, 0))

        # IP address - only shown when Connect is selected.
        self.host_label = tk.Label(frame, text="IP address:")
        self.host_var = tk.StringVar(value="127.0.0.1")
        self.host_entry = tk.Entry(frame, textvariable=self.host_var, width=28)
        self.host_label.grid(row=3, column=0, sticky="e", padx=(0, 8), pady=4)
        self.host_entry.grid(row=3, column=1, sticky="w", pady=4)

        # Port.
        tk.Label(frame, text="Port:").grid(row=4, column=0, sticky="e", padx=(0, 8), pady=4)
        self.port_var = tk.StringVar(value="5555")
        port_entry = tk.Entry(frame, textvariable=self.port_var, width=28)
        port_entry.grid(row=4, column=1, sticky="w", pady=4)

        # Error label for bad input.
        self.error_var = tk.StringVar(value="")
        tk.Label(frame, textvariable=self.error_var, fg="red").grid(
            row=5, column=0, columnspan=2, pady=(8, 0))

        def submit():
            password = self.password_var.get()
            mode = self.mode_var.get()
            host = self.host_var.get().strip()
            port_str = self.port_var.get()

            if not password:
                self.error_var.set("Password is required.")
                return
            try:
                port = int(port_str)
            except ValueError:
                self.error_var.set("Port must be a number.")
                return
            if mode == "Connect" and not host:
                self.error_var.set("IP address is required in Connect mode.")
                return

            self.error_var.set("")
            on_start(password, mode, host, port)

        start_btn = tk.Button(frame, text="Start", width=12, command=submit)
        start_btn.grid(row=6, column=0, columnspan=2, pady=(16, 0))

        password_entry.focus_set()
        self._on_mode_change()

    def _on_mode_change(self):
        # Hide the IP field when hosting, show it when connecting.
        if self.mode_var.get() == "Connect":
            self.host_label.grid()
            self.host_entry.grid()
        else:
            self.host_label.grid_remove()
            self.host_entry.grid_remove()

    def show_chat_screen(self):
        self._clear_container()

        frame = tk.Frame(self.container)
        frame.pack(fill=tk.BOTH, expand=True)

        # Read-only scrolling text area for the chat history.
        self.chat_display = scrolledtext.ScrolledText(frame, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 4))

        # Input row: text entry + Send button.
        input_row = tk.Frame(frame)
        input_row.pack(fill=tk.X, padx=8, pady=(0, 4))

        self.input_entry = tk.Entry(input_row)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", lambda e: self._on_send_clicked())

        send_btn = tk.Button(input_row, text="Send", command=self._on_send_clicked)
        send_btn.pack(side=tk.LEFT, padx=(8, 0))

        # Status bar at the bottom.
        self.status_var = tk.StringVar(value="")
        status_bar = tk.Label(frame, textvariable=self.status_var, anchor="w",
                              relief=tk.SUNKEN, bd=1)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.input_entry.focus_set()

    def _on_send_clicked(self):
        if self.input_entry is None or self.send_handler is None:
            return
        text = self.input_entry.get()
        if not text:
            return
        self.input_entry.delete(0, tk.END)
        self.send_handler(text)

    def set_send_handler(self, handler):
        self.send_handler = handler

    def display_sent(self, plaintext, ciphertext_hex):
        self._append_lines([
            "[You] Plaintext: " + plaintext,
            "      Ciphertext: " + ciphertext_hex,
            "",
        ])

    def display_received(self, ciphertext_hex, plaintext):
        self._append_lines([
            "[Peer] Ciphertext: " + ciphertext_hex,
            "       Plaintext: " + plaintext,
            "",
        ])

    def update_status(self, text):
        # Schedule on the main thread - the network thread also calls this.
        def do_update():
            if self.status_var is not None:
                self.status_var.set(text)
        self.root.after(0, do_update)

    def _append_lines(self, lines):
        # Schedule on the main thread because tkinter isn't thread-safe.
        def do_append():
            if self.chat_display is None:
                return
            self.chat_display.configure(state=tk.NORMAL)
            for line in lines:
                self.chat_display.insert(tk.END, line + "\n")
            self.chat_display.see(tk.END)
            self.chat_display.configure(state=tk.DISABLED)
        self.root.after(0, do_append)

    def _clear_container(self):
        for child in self.container.winfo_children():
            child.destroy()
        self.chat_display = None
        self.input_entry = None
        self.status_var = None

    def run(self):
        self.root.mainloop()
