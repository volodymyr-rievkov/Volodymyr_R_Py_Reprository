from struct import unpack_from, pack
from typing import Union
from numba import jit
from config import MD5_A, MD5_B, MD5_C, MD5_D, S, K

MASK32 = 0xFFFFFFFF

@jit(nopython=True)
def _left_rotate(x: int, amount: int) -> int:
    x &= MASK32
    return ((x << amount) | (x >> (32 - amount))) & MASK32

@jit(nopython=True)
def _process_chunk(A, B, C, D, M, K, S):
    A0, B0, C0, D0 = A, B, C, D
    for i in range(64):
        if i < 16:
            F = (B & C) | (~B & D)
            g = i
        elif i < 32:
            F = (D & B) | (~D & C)
            g = (5 * i + 1) % 16
        elif i < 48:
            F = B ^ C ^ D
            g = (3 * i + 5) % 16
        else:
            F = C ^ (B | ~D)
            g = (7 * i) % 16
        F = (F + A + K[i] + M[g]) & MASK32
        A, D, C, B = D, C, B, (B + _left_rotate(F, S[i])) & MASK32
    return (A0 + A) & MASK32, (B0 + B) & MASK32, (C0 + C) & MASK32, (D0 + D) & MASK32

class MD5:
    def __init__(self):
        self._A = MD5_A
        self._B = MD5_B
        self._C = MD5_C
        self._D = MD5_D
        self._K_tuple = tuple(K)
        self._S_tuple = tuple(S)
        self._buffer = bytearray()
        self._bits = 0

    def update(self, data: Union[bytes, bytearray, str]):
        if isinstance(data, str):
            data = data.encode("utf-8")
        self._buffer.extend(data)
        self._bits += len(data) * 8

        mv = self._buffer
        n_blocks = len(mv) // 64
        for i in range(n_blocks):
            offset = i * 64
            M = unpack_from("<16I", mv, offset)
            self._A, self._B, self._C, self._D = _process_chunk(
                self._A, self._B, self._C, self._D,
                M, self._K_tuple, self._S_tuple
            )
        del self._buffer[:n_blocks * 64]

    def _pad(self) -> bytes:
        padding = b"\x80"
        pad_len = ((56 - (len(self._buffer) + 1) % 64) % 64)
        padding += b"\x00" * pad_len
        padding += pack("<Q", self._bits)
        return padding

    def digest(self) -> bytes:
        saved_buf = bytes(self._buffer)
        saved_bits = self._bits
        saved_A, saved_B, saved_C, saved_D = self._A, self._B, self._C, self._D

        self.update(self._pad())
        result = pack("<4I", self._A, self._B, self._C, self._D)

        self._buffer = bytearray(saved_buf)
        self._bits = saved_bits
        self._A, self._B, self._C, self._D = saved_A, saved_B, saved_C, saved_D
        return result

    def hexdigest(self) -> str:
        return ''.join(f"{b:02x}" for b in self.digest())
