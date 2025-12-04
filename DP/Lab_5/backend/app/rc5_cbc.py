from .rc5 import rc5_encrypt_block, rc5_decrypt_block, rc5_key_schedule, BLOCK_SIZE
from .lcg import lcg_generate_stream
from fastapi import HTTPException, UploadFile
import numpy as np

CHUNK_SIZE = 1024 * 512 

def xor_bytes(a: bytes, b: bytes) -> bytes:
    a_arr = np.frombuffer(a, dtype=np.uint8)
    b_arr = np.frombuffer(b, dtype=np.uint8)
    return (a_arr ^ b_arr).tobytes()


def pad(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)


def unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    if pad_len == 0 or pad_len > BLOCK_SIZE:
        raise ValueError("Invalid padding")
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Invalid padding")
    return data[:-pad_len]


def generate_iv(block_size: int = BLOCK_SIZE) -> bytes:
    gen = lcg_generate_stream(block_size)
    iv_ints = [next(gen) % 256 for _ in range(block_size)]
    return bytes(iv_ints)


def rc5_cbc_encrypt(data: bytes, key: bytes) -> bytes:
    S = rc5_key_schedule(key)
    iv = generate_iv()
    enc_iv = rc5_encrypt_block(iv, S)
    prev = iv
    data = pad(data)
    ciphertext = bytearray(enc_iv)
    for i in range(0, len(data), BLOCK_SIZE):
        block = xor_bytes(data[i:i + BLOCK_SIZE], prev)
        enc_block = rc5_encrypt_block(block, S)
        ciphertext.extend(enc_block)
        prev = enc_block
    return bytes(ciphertext)


def rc5_cbc_decrypt(data: bytes, key: bytes) -> bytes:
    S = rc5_key_schedule(key)
    enc_iv = data[:BLOCK_SIZE]
    iv = rc5_decrypt_block(enc_iv, S)
    prev = iv
    plaintext = bytearray()
    for i in range(BLOCK_SIZE, len(data), BLOCK_SIZE):
        block = data[i:i + BLOCK_SIZE]
        dec = rc5_decrypt_block(block, S)
        plaintext.extend(xor_bytes(dec, prev))
        prev = block
    return unpad(bytes(plaintext))


async def encrypt_file_stream(upload_file: UploadFile, key: bytes):
    iv = generate_iv(BLOCK_SIZE)
    S = rc5_key_schedule(key)
    prev = iv
    yield rc5_encrypt_block(iv, S)
    
    leftover = bytearray()
    
    while chunk := await upload_file.read(CHUNK_SIZE):
        chunk = leftover + chunk
        process_len = (len(chunk) // BLOCK_SIZE) * BLOCK_SIZE
        
        ciphertext_chunk = bytearray()
        for i in range(0, process_len, BLOCK_SIZE):
            block = chunk[i:i + BLOCK_SIZE]
            enc_block = rc5_encrypt_block(xor_bytes(block, prev), S)
            prev = enc_block
            ciphertext_chunk.extend(enc_block)
        
        if ciphertext_chunk:
            yield bytes(ciphertext_chunk)
        
        leftover = chunk[process_len:]
    
    final_data = pad(bytes(leftover))
    final_chunk = bytearray()
    for i in range(0, len(final_data), BLOCK_SIZE):
        block = final_data[i:i + BLOCK_SIZE]
        enc_block = rc5_encrypt_block(xor_bytes(block, prev), S)
        prev = enc_block
        final_chunk.extend(enc_block)
    
    if final_chunk:
        yield bytes(final_chunk)
    
    await upload_file.close()


async def decrypt_file_stream(upload_file: UploadFile, key: bytes):
    S = rc5_key_schedule(key)
    enc_iv = await upload_file.read(BLOCK_SIZE)
    iv = rc5_decrypt_block(enc_iv, S)
    prev = iv
    
    leftover = bytearray()
    last_block = None  
    
    while chunk := await upload_file.read(CHUNK_SIZE):
        chunk = leftover + chunk
        chunk_len = len(chunk)
        process_len = (chunk_len // BLOCK_SIZE) * BLOCK_SIZE
        
        plaintext_chunk = bytearray()
        for i in range(0, process_len, BLOCK_SIZE):
            block = chunk[i:i+BLOCK_SIZE]
            dec_block = xor_bytes(rc5_decrypt_block(block, S), prev)
            prev = block
            
            if last_block is not None:
                plaintext_chunk.extend(last_block)
            
            last_block = dec_block
        
        if plaintext_chunk:
            yield bytes(plaintext_chunk)
        
        leftover = chunk[process_len:]
    
    if leftover and len(leftover) == BLOCK_SIZE:
        dec_block = xor_bytes(rc5_decrypt_block(leftover, S), prev)
        if last_block is not None:
            yield bytes(last_block)
        last_block = dec_block
    
    if last_block is not None:
        try:
            yield unpad(bytes(last_block))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid padding: {str(e)}")
    
    await upload_file.close()
