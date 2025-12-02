import pytest
import logging
import numpy as np
from app.rc5 import (
    rc5_constants,
    rc5_format,
    _rotl,
    _rotr,
    rc5_key_schedule,
    rc5_encrypt_block,
    rc5_decrypt_block,
    RC5_R
)
from tests_config import TEST_KEY, TEST_BLOCK

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_rc5_constants():
    logger.info("Starting test_rc5_constants")
    Pw, Qw = rc5_constants(16)
    assert Pw == 0xB7E1
    assert Qw == 0x9E37
    Pw, Qw = rc5_constants(32)
    assert Pw == 0xB7E15163
    assert Qw == 0x9E3779B9
    Pw, Qw = rc5_constants(64)
    assert Pw == 0xB7E151628AED2A6B
    assert Qw == 0x9E3779B97F4A7C15
    with pytest.raises(ValueError):
        rc5_constants(8)
    logger.info("Finished test_rc5_constants")

def test_rc5_format():
    logger.info("Starting test_rc5_format")
    assert rc5_format(16) == "<2H"
    assert rc5_format(32) == "<2I"
    assert rc5_format(64) == "<2Q"
    logger.info("Finished test_rc5_format")

def test_rotl_rotr():
    logger.info("Starting test_rotl_rotr")
    x = 0x12345678
    y = 4
    rotated = _rotl(x, y)
    back = _rotr(rotated, y)
    assert back == x
    logger.info("Finished test_rotl_rotr")

def test_rc5_key_schedule_shape():
    logger.info("Starting test_rc5_key_schedule_shape")
    S = rc5_key_schedule(TEST_KEY)
    assert isinstance(S, np.ndarray)
    assert len(S) == 2 * (RC5_R + 1)
    logger.info(f"rc5_key_schedule length: {len(S)}")
    logger.info("Finished test_rc5_key_schedule_shape")

def test_rc5_key_schedule_values():
    logger.info("Starting test_rc5_key_schedule_values")
    S = rc5_key_schedule(TEST_KEY)
    assert S[0] != 0
    assert S[-1] != 0
    logger.info("Finished test_rc5_key_schedule_values")

def test_rc5_encrypt_decrypt_block():
    logger.info("Starting test_rc5_encrypt_decrypt_block")
    S = rc5_key_schedule(TEST_KEY)
    block = TEST_BLOCK
    enc = rc5_encrypt_block(block, S)
    dec = rc5_decrypt_block(enc, S)
    assert dec == block
    logger.info("Finished test_rc5_encrypt_decrypt_block")

def test_rc5_encrypt_block_type_and_size():
    logger.info("Starting test_rc5_encrypt_block_type_and_size")
    S = rc5_key_schedule(TEST_KEY)
    block = TEST_BLOCK
    enc = rc5_encrypt_block(block, S)
    assert isinstance(enc, bytes)
    assert len(enc) == len(block)
    logger.info("Finished test_rc5_encrypt_block_type_and_size")

def test_rc5_decrypt_block_type_and_size():
    logger.info("Starting test_rc5_decrypt_block_type_and_size")
    S = rc5_key_schedule(TEST_KEY)
    block = TEST_BLOCK
    enc = rc5_encrypt_block(block, S)
    dec = rc5_decrypt_block(enc, S)
    assert isinstance(dec, bytes)
    assert len(dec) == len(block)
    logger.info("Finished test_rc5_decrypt_block_type_and_size")
