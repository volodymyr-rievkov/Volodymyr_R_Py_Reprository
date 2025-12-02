#Lab 1, LCG and Cesaro test parameters
LCG_TEST_N = 100
LCG_TEST_CHUNK_SIZE = 10
CESARO_TEST_N = 100  
CESARO_TEST_N_ODD = 7  

#Lab 2, MD5 test parameters
TEST_STRING = "The quick brown fox jumps over the lazy dog"
TEST_STRING_BYTES = TEST_STRING.encode("utf-8")
TEST_MD5_HEX = "9e107d9d372bb6826bd81d3542a419d6"

LARGE_TEST_DATA = b"A" * 1024

#Lab 3, RC5 test parameters
TEST_KEY = b"0123456789abcdef"
TEST_BLOCK = b"\x01\x02\x03\x04\x05\x06\x07\x08"

#Lab 4, RSA test parameters
TEST_DATA = b"The quick brown fox jumps over the lazy dog" * 1024