from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key, load_pem_public_key
)
from cryptography.exceptions import InvalidSignature

CHUNK_SIZE = 1024 * 1024  


def sign_stream(file_obj, private_key_pem: str) -> bytes:
    private_key = load_pem_private_key(private_key_pem.encode(), password=None)

    digest = hashes.Hash(hashes.SHA256())
    while chunk := file_obj.read(CHUNK_SIZE):
        digest.update(chunk)

    file_hash = digest.finalize()
    return private_key.sign(file_hash, hashes.SHA256())


def verify_stream(file_obj, public_key_pem: str, signature: bytes) -> bool:
    public_key = load_pem_public_key(public_key_pem.encode())

    digest = hashes.Hash(hashes.SHA256())
    while chunk := file_obj.read(CHUNK_SIZE):
        digest.update(chunk)

    file_hash = digest.finalize()

    try:
        public_key.verify(signature, file_hash, hashes.SHA256())
        return True
    except InvalidSignature:
        return False
