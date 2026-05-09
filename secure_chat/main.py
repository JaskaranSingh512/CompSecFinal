"""Main"""

import threading

from crypto_module import derive_key, encrypt, decrypt
from gui_module import ChatGUI
from network_module import PeerConnection


# Re-derive the key after every 10 messages (sent + received combined).
ROTATE_EVERY = 10


# Shared chat state. Keeping this as plain module-level variables
# instead of building a class for it.
password = None
current_key = None
epoch = 0
counter = 0
state_lock = threading.Lock()  # send and receive run on different threads

gui = None
network = None
connected = False


def maybe_rotate_key():
    """message counter and rotate the key once we hit 10."""
    global counter, epoch, current_key
    counter += 1
    if counter >= ROTATE_EVERY:
        epoch += 1
        counter = 0
        current_key = derive_key(password, epoch)


def update_status_bar():
    gui.update_status(f"Connected - epoch {epoch}")


def handle_send(text):
    if not connected:
        gui.update_status("Not connected yet - cannot send.")
        return

    with state_lock:
        try:
            blob = encrypt(text, current_key)
        except Exception as e:
            gui.update_status(f"Encrypt error: {e}")
            return
        try:
            network.send(blob)
        except Exception as e:
            gui.update_status(f"Send error: {e}")
            return
        ciphertext_hex = blob.hex()
        maybe_rotate_key()

    gui.display_sent(text, ciphertext_hex)
    update_status_bar()


def handle_receive(blob):
    with state_lock:
        try:
            text = decrypt(blob, current_key)
        except Exception as e:
            gui.update_status(f"Decrypt error (wrong password?): {e}")
            return
        ciphertext_hex = blob.hex()
        maybe_rotate_key()

    gui.display_received(ciphertext_hex, text)
    update_status_bar()


def handle_disconnect():
    global connected
    connected = False
    gui.update_status("Peer disconnected.")


def on_start(pw, mode, host, port):
    global password, current_key, epoch, counter, network

    password = pw
    epoch = 0
    counter = 0
    current_key = derive_key(password, epoch)

    network = PeerConnection(on_message_received=handle_receive)
    network.on_disconnect = handle_disconnect

    gui.show_chat_screen()
    gui.set_send_handler(handle_send)

    # host() blocks waiting for a peer, so do it on a background thread,
    # otherwise the GUI freezes.
    def setup():
        global connected
        try:
            if mode == "Host":
                gui.update_status(f"Hosting on port {port} - waiting for peer...")
                network.host(port)
            else:
                gui.update_status(f"Connecting to {host}:{port}...")
                network.connect(host, port)
        except Exception as e:
            gui.update_status(f"Connection failed: {e}")
            return
        connected = True
        update_status_bar()

    t = threading.Thread(target=setup)
    t.daemon = True
    t.start()


def on_window_close():
    if network is not None:
        try:
            network.close()
        except Exception:
            pass
    try:
        gui.root.destroy()
    except Exception:
        pass


def main():
    global gui
    gui = ChatGUI()
    gui.root.protocol("WM_DELETE_WINDOW", on_window_close)
    gui.show_startup_screen(on_start)
    gui.run()


if __name__ == "__main__":
    main()
