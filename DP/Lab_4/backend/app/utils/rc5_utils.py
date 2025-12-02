from fastapi import HTTPException, UploadFile
from typing import Optional
from .md5_utils import md5_from_file, md5_bytes
from config import RC5_B
from ..rc5_cbc import BLOCK_SIZE

KEY_BITS = RC5_B * 8
MAX_FILE_SIZE = 101 * 1024 * 1024  
MIN_ENCRYPTED_SIZE = BLOCK_SIZE * 2  


async def derive_key_from_passphrase(passphrase: UploadFile, key_bits: int = KEY_BITS) -> bytes:
    h = await md5_from_file(passphrase, hex=False)  

    if key_bits == 64:
        return h[-8:]
    elif key_bits == 128:
        return h
    elif key_bits == 256:
        h2 = md5_bytes(h[:16])
        return h + h2
    else:
        raise ValueError("Unsupported key length")


def validate_passphrase(passfile: Optional[UploadFile]) -> None:
    if not passfile:
        raise HTTPException(status_code=400, detail="Passfile is required")
    
    size = get_file_size(passfile)
    if size == 0:
        raise HTTPException(status_code=400, detail="Passfile cannot be empty")


def get_file_size(file: UploadFile) -> int:
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    return size


def validate_file_for_encryption(file: UploadFile) -> None:
    if not file:
        raise HTTPException(status_code=400, detail="File is required")

    size = get_file_size(file)
    
    if size == 0:
        raise HTTPException(status_code=400, detail="File cannot be empty")

    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File is too large (maximum {MAX_FILE_SIZE // (1024 * 1024)}MB)"
        )


def validate_file_for_decryption(encrypted_file: UploadFile) -> None:
    if not encrypted_file:
        raise HTTPException(status_code=400, detail="Encrypted file is required")
    
    size = get_file_size(encrypted_file)
    
    if size == 0:
        raise HTTPException(status_code=400, detail="File cannot be empty")

    if size < MIN_ENCRYPTED_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File is too small for decryption (minimum {MIN_ENCRYPTED_SIZE} bytes)"
        )

    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File is too large (maximum {MAX_FILE_SIZE // (1024 * 1024)}MB)"
        )

    if size % BLOCK_SIZE != 0:
        raise HTTPException(
            status_code=400, 
            detail="Invalid encrypted file format (size must be a multiple of block size)"
        )


def handle_decryption_error(error: Exception) -> HTTPException:
    if isinstance(error, ValueError):
        return HTTPException(
            status_code=400,
            detail=f"Validation error: {str(error)}"
        )

    return HTTPException(
        status_code=500,
        detail=f"Decryption error: {str(error)}"
    )


def handle_encryption_error(error: Exception) -> HTTPException:
    
    if isinstance(error, ValueError):
        return HTTPException(status_code=400, detail=f"Validation error: {str(error)}")
    
    return HTTPException(status_code=500, detail=f"Encryption error: {str(error)}")