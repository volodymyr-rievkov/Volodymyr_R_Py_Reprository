import pytest
import logging
from io import BytesIO
from fastapi import UploadFile, HTTPException

from app.md5 import MD5
from app.utils.md5_utils import validate_md5_hash, md5_from_file, md5_bytes
from tests_config import TEST_STRING, TEST_STRING_BYTES, TEST_MD5_HEX, LARGE_TEST_DATA

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_md5_digest():
    logger.info("Testing MD5 digest")
    md = MD5()
    md.update(TEST_STRING)
    digest = md.digest()
    assert isinstance(digest, bytes)
    assert digest == bytes.fromhex(TEST_MD5_HEX)
    logger.info(f"MD5 digest: {digest.hex()}")

def test_md5_hexdigest():
    logger.info("Testing MD5 hexdigest")
    md = MD5()
    md.update(TEST_STRING)
    hexdigest = md.hexdigest()
    assert isinstance(hexdigest, str)
    assert hexdigest == TEST_MD5_HEX
    logger.info(f"MD5 hexdigest: {hexdigest}")

def test_md5_multiple_updates():
    logger.info("Testing MD5 with multiple updates")
    md = MD5()
    md.update("The quick brown ")
    md.update("fox jumps over ")
    md.update("the lazy dog")
    assert md.hexdigest() == TEST_MD5_HEX
    logger.info(f"MD5 multiple updates: {md.hexdigest()}")

def test_md5_empty():
    logger.info("Testing MD5 empty input")
    md = MD5()
    md.update("")
    digest = md.digest()
    hexdigest = md.hexdigest()
    assert isinstance(digest, bytes)
    assert isinstance(hexdigest, str)
    logger.info(f"MD5 empty string hexdigest: {hexdigest}")

def test_md5_bytes():
    logger.info("Testing md5_bytes utility")
    result = md5_bytes(TEST_STRING_BYTES)
    md = MD5()
    md.update(TEST_STRING_BYTES)
    assert isinstance(result, bytes)
    assert result == md.digest()
    logger.info(f"md5_bytes result: {result.hex()}")

@pytest.mark.asyncio
async def test_md5_from_file_hexdigest():
    logger.info("Testing md5_from_file hexdigest")
    file_like = BytesIO(TEST_STRING_BYTES)
    upload_file = UploadFile(filename="test.txt", file=file_like)
    result_hex = await md5_from_file(upload_file)
    assert isinstance(result_hex, str)
    assert result_hex == TEST_MD5_HEX
    logger.info(f"md5_from_file hexdigest: {result_hex}")

@pytest.mark.asyncio
async def test_md5_from_file_bytes():
    logger.info("Testing md5_from_file bytes output")
    file_like = BytesIO(TEST_STRING_BYTES)
    upload_file = UploadFile(filename="test.txt", file=file_like)
    result_bytes = await md5_from_file(upload_file, hex=False)
    md = MD5()
    md.update(TEST_STRING_BYTES)
    assert isinstance(result_bytes, bytes)
    assert result_bytes == md.digest()
    logger.info(f"md5_from_file bytes: {result_bytes.hex()}")

def test_validate_md5_hash_valid():
    logger.info("Testing validate_md5_hash valid")
    validate_md5_hash(TEST_MD5_HEX)
    logger.info("validate_md5_hash valid passed")

def test_validate_md5_hash_empty():
    logger.info("Testing validate_md5_hash empty")
    with pytest.raises(HTTPException):
        validate_md5_hash("")
    logger.info("validate_md5_hash empty raised HTTPException")

def test_validate_md5_hash_invalid():
    logger.info("Testing validate_md5_hash invalid format")
    with pytest.raises(HTTPException):
        validate_md5_hash("invalidmd5hash123")
    logger.info("validate_md5_hash invalid raised HTTPException")

@pytest.mark.asyncio
async def test_md5_large_data():
    logger.info("Testing MD5 with large data")
    file_like = BytesIO(LARGE_TEST_DATA)
    upload_file = UploadFile(filename="large_test.txt", file=file_like)
    result_hex = await md5_from_file(upload_file)
    assert isinstance(result_hex, str)
    assert len(result_hex) == 32
    logger.info(f"MD5 large data hexdigest: {result_hex}")

    file_like = BytesIO(LARGE_TEST_DATA)
    upload_file = UploadFile(filename="large_test.txt", file=file_like)
    result_bytes = await md5_from_file(upload_file, hex=False)
    assert isinstance(result_bytes, bytes)
    assert len(result_bytes) == 16
    logger.info(f"MD5 large data digest length: {len(result_bytes)}")
