"""Crypto stuff for the chat: derive a key, encrypt, decrypt."""

import os

from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


# Both sides use the same fixed salt because they share the password.
SALT = b'CS4173_FixedSalt'
PBKDF2_ITERATIONS = 200_000
KEY_SIZE = 16    # 128-bit AES key
IV_SIZE = 16
BLOCK_SIZE = 128  # bits, used by the PKCS#7 padder


def derive_key(password, epoch=0):
    # Mix the epoch into the salt so each rotation gives a brand new key.
    salt = SALT + epoch.to_bytes(8, 'big')
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(password.encode('utf-8'))


def encrypt(plaintext, key):
    # Fresh random IV every time so the same message looks different each send.
    iv = os.urandom(IV_SIZE)

    padder = padding.PKCS7(BLOCK_SIZE).padder()
    padded = padder.update(plaintext.encode('utf-8')) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()

    # Stick the IV on the front so the receiver can pull it back off.
    return iv + ciphertext


def decrypt(blob, key):
    iv = blob[:IV_SIZE]
    ciphertext = blob[IV_SIZE:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(BLOCK_SIZE).unpadder()
    plaintext = unpadder.update(padded) + unpadder.finalize()

    return plaintext.decode('utf-8')
