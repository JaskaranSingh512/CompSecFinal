"""TCP connection between two peers, with simple length-prefixed messages."""

import socket
import struct
import threading


class PeerConnection:
    """One side calls host(), the other calls connect(). After that, send()
    sends a message and the background thread calls on_message_received
    whenever a full message arrives."""

    def __init__(self, on_message_received):
        self.on_message_received = on_message_received
        # main.py sets this so we can show a status when the peer drops.
        self.on_disconnect = None

        self.sock = None
        self.listen_sock = None
        self.closed = False

    def host(self, port):
        # Listen on the port and wait for one peer to connect.
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_sock.bind(('', port))
        self.listen_sock.listen(1)

        conn, _addr = self.listen_sock.accept()
        self.sock = conn

        self.listen_sock.close()
        self.listen_sock = None

        self._start_recv_thread()

    def connect(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self._start_recv_thread()

    def send(self, blob):
        # 4-byte big-endian length prefix, then the blob itself.
        header = struct.pack('>I', len(blob))
        self.sock.sendall(header + blob)

    def _start_recv_thread(self):
        t = threading.Thread(target=self._recv_loop)
        t.daemon = True
        t.start()

    def _recv_n(self, n):
        # Read exactly n bytes, or return None if the connection closed.
        data = b''
        while len(data) < n:
            try:
                chunk = self.sock.recv(n - len(data))
            except OSError:
                return None
            if not chunk:
                return None
            data += chunk
        return data

    def _recv_loop(self):
        while not self.closed:
            header = self._recv_n(4)
            if header is None:
                break
            length = struct.unpack('>I', header)[0]
            payload = self._recv_n(length)
            if payload is None:
                break
            self.on_message_received(payload)

        # If we exited because the peer dropped (not because we called close),
        # let main.py know so it can update the status bar.
        if not self.closed and self.on_disconnect is not None:
            self.on_disconnect()

    def close(self):
        self.closed = True
        for s in (self.sock, self.listen_sock):
            if s is not None:
                try:
                    s.close()
                except OSError:
                    pass
        self.sock = None
        self.listen_sock = None
