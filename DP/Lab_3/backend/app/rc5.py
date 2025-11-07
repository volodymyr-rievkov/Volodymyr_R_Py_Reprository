import struct
import numpy as np
from numba import njit
from config import RC5_W, RC5_R

WORD_MASK = (1 << RC5_W) - 1
BLOCK_SIZE = 2 * (RC5_W // 8)


def rc5_constants(w: int = RC5_W) -> tuple[int, int]:
    if w == 16:
        return 0xB7E1, 0x9E37
    elif w == 32:
        return 0xB7E15163, 0x9E3779B9
    elif w == 64:
        return 0xB7E151628AED2A6B, 0x9E3779B97F4A7C15
    else:
        raise ValueError("Unsupported word size")


def rc5_format(w: int) -> str:
    return "<2H" if w == 16 else "<2I" if w == 32 else "<2Q"


@njit(cache=True)
def _rotl(x: int, y: int) -> int:
    return ((x << (y & (RC5_W - 1))) | (x >> (RC5_W - (y & (RC5_W - 1))))) & WORD_MASK


@njit(cache=True)
def _rotr(x: int, y: int) -> int:
    return ((x >> (y & (RC5_W - 1))) | (x << (RC5_W - (y & (RC5_W - 1))))) & WORD_MASK


def rc5_key_schedule(key: bytes, w: int = RC5_W, r: int = RC5_R) -> np.ndarray:
    Pw, Qw = rc5_constants(w)
    u = w // 8
    c = max(1, (len(key) + u - 1) // u)
    dtype = np.uint32 if w == 32 else np.uint16 if w == 16 else np.uint64

    L = np.zeros(c, dtype=dtype)
    for i in range(len(key)):
        L[i // u] = (L[i // u] | (key[i] << (8 * (i % u)))) & WORD_MASK

    t = 2 * (r + 1)
    S = np.zeros(t, dtype=dtype)
    S[0] = Pw
    for i in range(1, t):
        S[i] = (int(S[i - 1]) + Qw) & WORD_MASK

    A = B = i = j = 0
    n = 3 * max(t, c)
    for _ in range(n):
        A = S[i] = _rotl((int(S[i]) + A + B) & WORD_MASK, 3)
        B = L[j] = _rotl((int(L[j]) + A + B) & WORD_MASK, int((A + B) & (w - 1)))
        i = (i + 1) % t
        j = (j + 1) % c

    return S


@njit(cache=True)
def _encrypt_block(A: int, B: int, S: np.ndarray, w: int, r: int) -> tuple[int, int]:
    A = (A + S[0]) & WORD_MASK
    B = (B + S[1]) & WORD_MASK
    for i in range(1, r + 1):
        A = (_rotl(A ^ B, B) + S[2 * i]) & WORD_MASK
        B = (_rotl(B ^ A, A) + S[2 * i + 1]) & WORD_MASK
    return A, B


@njit(cache=True)
def _decrypt_block(A: int, B: int, S: np.ndarray, w: int, r: int) -> tuple[int, int]:
    for i in range(r, 0, -1):
        B = _rotr((B - S[2 * i + 1]) & WORD_MASK, A) ^ A
        A = _rotr((A - S[2 * i]) & WORD_MASK, B) ^ B
    A = (A - S[0]) & WORD_MASK
    B = (B - S[1]) & WORD_MASK
    return A, B


def rc5_encrypt_block(block: bytes, S: np.ndarray, w: int = RC5_W, r: int = RC5_R) -> bytes:
    A, B = struct.unpack(rc5_format(w), block)
    A, B = _encrypt_block(A, B, S, w, r)
    return struct.pack(rc5_format(w), A, B)


def rc5_decrypt_block(block: bytes, S: np.ndarray, w: int = RC5_W, r: int = RC5_R) -> bytes:
    A, B = struct.unpack(rc5_format(w), block)
    A, B = _decrypt_block(A, B, S, w, r)
    return struct.pack(rc5_format(w), A, B)
