import pytest
import logging
from io import BytesIO
from fastapi import UploadFile

from app.utils.rsa_utils import generate_rsa_keys
from app.rsa import encrypt_rsa_stream, decrypt_rsa_stream
from app.rsa_hybrid import encrypt_hybrid_stream, decrypt_hybrid_stream
from tests_config import LARGE_TEST_DATA as TEST_DATA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_generate_rsa_keys():
    logger.info("Testing RSA key generation")
    private_key, public_key = generate_rsa_keys(2048)
    assert private_key.startswith("-----BEGIN PRIVATE KEY-----")
    assert public_key.startswith("-----BEGIN PUBLIC KEY-----")
    logger.info("RSA key generation passed")

def test_rsa_encrypt_decrypt_stream():
    logger.info("Testing RSA encrypt/decrypt stream")
    private_key, public_key = generate_rsa_keys(2048)
    file_like = BytesIO(TEST_DATA)
    encrypted_chunks = list(encrypt_rsa_stream(file_like, public_key))
    assert all(isinstance(c, bytes) for c in encrypted_chunks)
    encrypted_data = b"".join(encrypted_chunks)
    assert encrypted_data != TEST_DATA
    file_like = BytesIO(encrypted_data)
    decrypted_chunks = list(decrypt_rsa_stream(file_like, private_key))
    decrypted_data = b"".join(decrypted_chunks)
    assert decrypted_data == TEST_DATA
    logger.info("RSA encrypt/decrypt stream passed")

def test_rsa_hybrid_encrypt_decrypt_stream():
    logger.info("Testing RSA-hybrid encrypt/decrypt stream")
    private_key, public_key = generate_rsa_keys(2048)
    file_like = BytesIO(TEST_DATA)
    encrypted_chunks = list(encrypt_hybrid_stream(file_like, public_key))
    assert all(isinstance(c, bytes) for c in encrypted_chunks)
    encrypted_data = b"".join(encrypted_chunks)
    assert encrypted_data != TEST_DATA
    file_like = BytesIO(encrypted_data)
    decrypted_chunks = list(decrypt_hybrid_stream(file_like, private_key))
    decrypted_data = b"".join(decrypted_chunks)
    assert decrypted_data == TEST_DATA
    logger.info("RSA-hybrid encrypt/decrypt stream passed")

@pytest.mark.asyncio
async def test_rsa_stream_uploadfile():
    logger.info("Testing RSA encrypt/decrypt with UploadFile")
    private_key, public_key = generate_rsa_keys(2048)
    upload_file = UploadFile(filename="test.txt", file=BytesIO(TEST_DATA))
    encrypted_chunks = list(encrypt_rsa_stream(upload_file.file, public_key))
    encrypted_data = b"".join(encrypted_chunks)
    upload_file.file = BytesIO(encrypted_data)
    decrypted_chunks = list(decrypt_rsa_stream(upload_file.file, private_key))
    decrypted_data = b"".join(decrypted_chunks)
    assert decrypted_data == TEST_DATA
    logger.info("RSA UploadFile encrypt/decrypt passed")

@pytest.mark.asyncio
async def test_rsa_hybrid_uploadfile():
    logger.info("Testing RSA-hybrid encrypt/decrypt with UploadFile")
    private_key, public_key = generate_rsa_keys(2048)
    upload_file = UploadFile(filename="test.txt", file=BytesIO(TEST_DATA))
    encrypted_chunks = list(encrypt_hybrid_stream(upload_file.file, public_key))
    encrypted_data = b"".join(encrypted_chunks)
    upload_file.file = BytesIO(encrypted_data)
    decrypted_chunks = list(decrypt_hybrid_stream(upload_file.file, private_key))
    decrypted_data = b"".join(decrypted_chunks)
    assert decrypted_data == TEST_DATA
    logger.info("RSA-hybrid UploadFile encrypt/decrypt passed")

def test_rsa_hybrid_unique_encryption():
    logger.info("Testing RSA-hybrid produces different output for same input")
    private_key, public_key = generate_rsa_keys(2048)
    file_like1 = BytesIO(TEST_DATA)
    file_like2 = BytesIO(TEST_DATA)
    enc1 = b"".join(encrypt_hybrid_stream(file_like1, public_key))
    enc2 = b"".join(encrypt_hybrid_stream(file_like2, public_key))
    assert enc1 != enc2
    logger.info("RSA-hybrid uniqueness test passed")
