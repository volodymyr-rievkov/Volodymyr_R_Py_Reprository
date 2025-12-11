import pytest
import logging
import asyncio
from fastapi import UploadFile, HTTPException
from io import BytesIO

from app.rc5_cbc import (
    xor_bytes,
    pad,
    unpad,
    generate_iv,
    rc5_cbc_encrypt,
    rc5_cbc_decrypt,
    encrypt_file_stream,
    decrypt_file_stream
)
from app.rc5 import BLOCK_SIZE, rc5_key_schedule


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEST_KEY = b"supersecretkey"
TEST_DATA = b"Hello RC5 CBC mode!!!"


def test_xor_bytes():
    logger.info("Starting test_xor_bytes")
    a = b"\x0f\x0f\x0f"
    b = b"\xf0\xf0\xf0"
    result = xor_bytes(a, b)
    assert result == b"\xff\xff\xff"
    logger.info("Finished test_xor_bytes")


def test_pad_unpad_correct():
    logger.info("Starting test_pad_unpad_correct")
    data = b"12345"
    padded = pad(data, BLOCK_SIZE)
    assert len(padded) % BLOCK_SIZE == 0
    assert unpad(padded) == data
    logger.info("Finished test_pad_unpad_correct")


def test_unpad_invalid_padding():
    logger.info("Starting test_unpad_invalid_padding")
    with pytest.raises(ValueError):
        unpad(b"\x01\x02\x03")
    logger.info("Finished test_unpad_invalid_padding")


def test_generate_iv_length():
    logger.info("Starting test_generate_iv_length")
    iv = generate_iv(BLOCK_SIZE)
    assert isinstance(iv, bytes)
    assert len(iv) == BLOCK_SIZE
    logger.info("Finished test_generate_iv_length")


def test_rc5_cbc_encrypt_decrypt_symmetry():
    logger.info("Starting test_rc5_cbc_encrypt_decrypt_symmetry")
    encrypted = rc5_cbc_encrypt(TEST_DATA, TEST_KEY)
    decrypted = rc5_cbc_decrypt(encrypted, TEST_KEY)
    assert decrypted == TEST_DATA
    logger.info("Finished test_rc5_cbc_encrypt_decrypt_symmetry")


def test_rc5_cbc_encrypt_consistent_output():
    logger.info("Starting test_rc5_cbc_encrypt_consistent_output")
    enc1 = rc5_cbc_encrypt(TEST_DATA, TEST_KEY)
    enc2 = rc5_cbc_encrypt(TEST_DATA, TEST_KEY)
    assert enc1 == enc2  
    logger.info("Finished test_rc5_cbc_encrypt_consistent_output")



@pytest.mark.asyncio
async def test_encrypt_file_stream_round_trip():
    logger.info("Starting test_encrypt_file_stream_round_trip")
    upload = UploadFile(filename="data.bin", file=BytesIO(TEST_DATA))
    chunks = []
    async for chunk in encrypt_file_stream(upload, TEST_KEY):
        chunks.append(chunk)

    encrypted = b"".join(chunks)

    upload_dec = UploadFile(filename="data.bin", file=BytesIO(encrypted))
    result = bytearray()
    async for chunk in decrypt_file_stream(upload_dec, TEST_KEY):
        result.extend(chunk)

    assert bytes(result) == TEST_DATA
    logger.info("Finished test_encrypt_file_stream_round_trip")


@pytest.mark.asyncio
async def test_streaming_chunk_splitting():
    logger.info("Starting test_streaming_chunk_splitting")
    data = b"A" * (BLOCK_SIZE + 10)

    upload = UploadFile(filename="file", file=BytesIO(data))
    encrypted_chunks = []
    async for chunk in encrypt_file_stream(upload, TEST_KEY):
        encrypted_chunks.append(chunk)
    encrypted = b"".join(encrypted_chunks)

    assert len(encrypted) % BLOCK_SIZE == 0

    upload2 = UploadFile(filename="file", file=BytesIO(encrypted))
    result = bytearray()
    async for chunk in decrypt_file_stream(upload2, TEST_KEY):
        result.extend(chunk)

    assert bytes(result) == data
    logger.info("Finished test_streaming_chunk_splitting")


@pytest.mark.asyncio
async def test_invalid_padding_raises_http_exception():
    logger.info("Starting test_invalid_padding_raises_http_exception")
    _ = rc5_key_schedule(TEST_KEY)
    iv = generate_iv()
    bad_cipher = iv + b"\x00" * BLOCK_SIZE  

    upload = UploadFile(filename="bad.bin", file=BytesIO(bad_cipher))

    with pytest.raises(HTTPException):
        async for _ in decrypt_file_stream(upload, TEST_KEY):
            raise AssertionError("Stream should not yield any data")


    logger.info("Finished test_invalid_padding_raises_http_exception")
