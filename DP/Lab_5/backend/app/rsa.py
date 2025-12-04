from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from config import HASH_SIZE_BYTES

def encrypt_rsa_stream(file_obj, public_key_pem):
    public_key = serialization.load_pem_public_key(public_key_pem.encode())
    rsa_block_size = public_key.key_size // 8 - 2*HASH_SIZE_BYTES - 2

    def generator():
        while True:
            block = file_obj.read(rsa_block_size)
            if not block:
                break
            yield public_key.encrypt(
                block,
                padding.OAEP(
                    mgf=padding.MGF1(hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
    return generator()


def decrypt_rsa_stream(file_obj, private_key_pem):
    private_key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
    rsa_block_size = private_key.key_size // 8

    def generator():
        while True:
            block = file_obj.read(rsa_block_size)
            if not block:
                break
            yield private_key.decrypt(
                block,
                padding.OAEP(
                    mgf=padding.MGF1(hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
    return generator()
