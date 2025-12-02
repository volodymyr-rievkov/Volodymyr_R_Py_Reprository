import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

AES_BLOCK = 64 * 1024

def encrypt_hybrid_stream(file_obj, public_key_pem):
    public_key = serialization.load_pem_public_key(public_key_pem.encode())

    aes_key = os.urandom(32)
    aes_iv = os.urandom(16)

    encrypted_header = public_key.encrypt(
        aes_key + aes_iv,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(aes_iv))
    encryptor = cipher.encryptor()

    def generator():
        yield encrypted_header
        while True:
            block = file_obj.read(AES_BLOCK)
            if not block:
                break
            yield encryptor.update(block)

    return generator()


def decrypt_hybrid_stream(file_obj, private_key_pem):
    private_key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
    rsa_block_size = private_key.key_size // 8

    encrypted_header = file_obj.read(rsa_block_size)
    aes_key_iv = private_key.decrypt(
        encrypted_header,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    aes_key = aes_key_iv[:32]
    aes_iv = aes_key_iv[32:]

    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(aes_iv))
    decryptor = cipher.decryptor()

    def generator():
        while True:
            block = file_obj.read(AES_BLOCK)
            if not block:
                break
            yield decryptor.update(block)

    return generator()
