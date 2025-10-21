from struct import unpack, pack
from config import MD5_A, MD5_B, MD5_C, MD5_D, S, K

def _process_chunk(chunk, a0, b0, c0, d0):
    M = unpack("<16I", chunk)
    A, B, C, D = a0, b0, c0, d0
    S_local, K_local = S, K
    for i in range(64):
        if i < 16:
            F = (B & C) | (~B & D)
            g = i
        elif i < 32:
            F = (D & B) | (~D & C)
            g = (5 * i + 1) & 0x0F
        elif i < 48:
            F = B ^ C ^ D
            g = (3 * i + 5) & 0x0F
        else:
            F = C ^ (B | ~D)
            g = (7 * i) & 0x0F
        F = (F + A + K_local[i] + M[g]) & 0xFFFFFFFF
        A, D, C, B = D, C, B, (B + ((F << S_local[i]) | (F >> (32 - S_local[i])))) & 0xFFFFFFFF
    return (
        (a0 + A) & 0xFFFFFFFF,
        (b0 + B) & 0xFFFFFFFF,
        (c0 + C) & 0xFFFFFFFF,
        (d0 + D) & 0xFFFFFFFF,
    )

def md5_stream(data_iter, total_bits=None):
    a0, b0, c0, d0 = MD5_A, MD5_B, MD5_C, MD5_D
    buffer = bytearray()
    processed_bits = 0
    for chunk in data_iter:
        processed_bits += len(chunk) * 8
        buffer.extend(chunk)
        view = memoryview(buffer)
        offset = 0
        full_blocks = (len(view) // 64) * 64
        while offset < full_blocks:
            a0, b0, c0, d0 = _process_chunk(view[offset:offset + 64], a0, b0, c0, d0)
            offset += 64
        buffer = buffer[offset:]
    buffer.extend(b"\x80")
    while len(buffer) % 64 != 56:
        buffer.append(0)
    buffer.extend(pack("<Q", total_bits or processed_bits))
    view = memoryview(buffer)
    for i in range(0, len(view), 64):
        a0, b0, c0, d0 = _process_chunk(view[i:i + 64], a0, b0, c0, d0)
    return ''.join(f'{x:02x}' for x in pack("<4I", a0, b0, c0, d0))

def md5_from_string(text, chunk_size=65536):
    data = text.encode()
    def iter_bytes():
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]
    return md5_stream(iter_bytes(), len(data) * 8)

async def md5_from_file(upload_file, chunk_size=1024*1024):
    a0, b0, c0, d0 = MD5_A, MD5_B, MD5_C, MD5_D
    leftover = bytearray()
    total_bits = 0
    while chunk := await upload_file.read(chunk_size):
        total_bits += len(chunk) * 8
        leftover.extend(chunk)
        view = memoryview(leftover)
        full_blocks = (len(view) // 64) * 64
        offset = 0
        while offset < full_blocks:
            a0, b0, c0, d0 = _process_chunk(view[offset:offset + 64], a0, b0, c0, d0)
            offset += 64
        leftover = leftover[offset:]
    leftover.extend(b"\x80")
    while len(leftover) % 64 != 56:
        leftover.append(0)
    leftover.extend(pack("<Q", total_bits))
    view = memoryview(leftover)
    for i in range(0, len(view), 64):
        a0, b0, c0, d0 = _process_chunk(view[i:i + 64], a0, b0, c0, d0)
    return ''.join(f'{x:02x}' for x in pack("<4I", a0, b0, c0, d0))
