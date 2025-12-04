from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives import serialization


def generate_dsa_keys(key_size: int = 2048):
    private_key = dsa.generate_private_key(key_size=key_size)
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    return private_pem, public_pem
