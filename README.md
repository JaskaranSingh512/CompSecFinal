# Secure Chat

A small two-person chat program. Messages are encrypted end-to-end with
AES-128-CBC using a key derived from a shared password.

## Requirements

- Python 3.8 or newer
- The `cryptography` package
- `tkinter` (ships with Python on Mac/Windows; on Linux: `sudo apt install python3-tk`)

Install the one third-party dependency:

```
pip install cryptography
```

## How to run

You need two terminals (or two computers on the same network). One side
**hosts** and the other **connects**. Start the host first, then the
connecting side. Both sides must type in the **same password**.

### Terminal 1 — Alice (Host)

```
cd secure_chat
python main.py
```

In the GUI:

1. Type a password (e.g. `hunter2`)
2. Select **Host**
3. Leave the port at `5555`
4. Click **Start**

The status bar shows `Hosting on port 5555 - waiting for peer...`.

### Terminal 2 — Bob (Connect)

```
cd secure_chat
python main.py
```

In the GUI:

1. Type the **same password** (`hunter2`)
2. Select **Connect**
3. Leave the IP address at `127.0.0.1` (or use Alice's IP if she's on
   another machine)
4. Leave the port at `5555`
5. Click **Start**

Both status bars now read `Connected - epoch 0`. Type a message in the
input box and hit Enter (or click Send). Both sides see the ciphertext
that went over the wire and the plaintext that was decrypted.

## Notes

- The same plaintext typed twice will produce different ciphertexts
  because a fresh random IV is used for every message.
- After every 10 messages (sent + received combined) both sides
  re-derive a new AES key from the password and bump the epoch shown
  in the status bar.
- If the peer disconnects, the status bar says so - the program does
  not crash.
- Closing the window cleanly closes the socket.

## Use of AI

-This readme files was made with the help of Opus 4.7 in cursor. - prompt - "Audit the codebase and give me a list of what i need to add to the readme to make sure everything is mentioned in order fro this program to work on a diffrent device
-Cursor was alos used to autocomplete code in multiple instances within the codebase, as well as suggestions.
-Cursor was also used for research on how to implemets certain programs and debuggung, for example prompt- "what is the code i have added the crypotography import libaray but i am having issues, here is the error, investigate and report how i can fix this".
