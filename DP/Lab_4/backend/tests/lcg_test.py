import pytest
import logging
from app.lcg import (
    lcg_generate_stream,
    lcg_stream,
    get_lcg_params,
    find_period,
    gcd,
    cesaro_test_stream
)
from config import M, A, C, X0
from tests_config import LCG_TEST_N, LCG_TEST_CHUNK_SIZE, CESARO_TEST_N, CESARO_TEST_N_ODD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_lcg_generate_stream_length():
    logger.info("Testing lcg_generate_stream length and range")
    stream = list(lcg_generate_stream(LCG_TEST_N))
    assert len(stream) == LCG_TEST_N
    for x in stream:
        assert 0 <= x < M
    logger.info(f"Generated {len(stream)} numbers within range 0..{M-1}")

def test_lcg_generate_zero():
    logger.info("Testing lcg_generate_stream with n=0")
    assert list(lcg_generate_stream(0)) == []
    logger.info("lcg_generate_stream returned empty list as expected")

def test_lcg_stream_chunks():
    logger.info("Testing lcg_stream chunking")
    chunks = list(lcg_stream(LCG_TEST_N, LCG_TEST_CHUNK_SIZE))
    numbers = []
    for chunk in chunks:
        numbers.extend(int(x) for x in chunk.split("\n") if x)
    assert len(numbers) == LCG_TEST_N
    logger.info(f"Generated stream in {len(chunks)} chunks, total numbers: {len(numbers)}")

def test_lcg_stream_small_chunk():
    logger.info("Testing lcg_stream with chunk_size > n")
    chunks = list(lcg_stream(5, chunk_size=10))
    numbers = [int(x) for chunk in chunks for x in chunk.split("\n") if x]
    assert numbers == list(lcg_generate_stream(5))
    logger.info(f"Stream with n=5 and chunk_size=10 generated correctly")

def test_get_lcg_params():
    logger.info("Testing get_lcg_params")
    params = get_lcg_params()
    assert params["M"] == M
    assert params["A"] == A
    assert params["C"] == C
    assert params["X0"] == X0
    logger.info(f"LCG params: {params}")

def test_find_period_positive():
    logger.info("Testing find_period")
    period = find_period()
    assert period > 0
    stream = list(lcg_generate_stream(period * 2))
    assert stream[:period] == stream[period:2*period]
    logger.info(f"Found period: {period}")

def test_gcd_basic():
    logger.info("Testing gcd function")
    assert gcd(10, 5) == 5
    assert gcd(17, 13) == 1
    assert gcd(0, 5) == 5
    assert gcd(5, 0) == 5
    logger.info("gcd basic tests passed")

def test_gcd_negative():
    logger.info("Testing gcd with negative numbers")
    assert gcd(-10, 5) == 5
    assert gcd(10, -5) == 5
    assert gcd(-10, -5) == 5
    logger.info("gcd negative tests passed")

def test_cesaro_test_stream_basic():
    logger.info("Testing cesaro_test_stream with even N")
    pi_est = cesaro_test_stream(CESARO_TEST_N)
    assert pi_est is not None
    assert isinstance(pi_est, float)
    logger.info(f"Estimated pi: {pi_est}")

def test_cesaro_test_stream_odd():
    logger.info("Testing cesaro_test_stream with odd N (should raise ValueError)")
    with pytest.raises(ValueError):
        cesaro_test_stream(CESARO_TEST_N_ODD)
    logger.info("ValueError correctly raised for odd N")

def test_cesaro_zero():
    logger.info("Testing cesaro_test_stream with N=0")
    assert cesaro_test_stream(0) is None
    logger.info("cesaro_test_stream returned None as expected for N=0")
