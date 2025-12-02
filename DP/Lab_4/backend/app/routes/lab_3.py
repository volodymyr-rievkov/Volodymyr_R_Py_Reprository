from fastapi.responses import StreamingResponse
from urllib.parse import quote
from fastapi import APIRouter, File, UploadFile, HTTPException
from ..utils.rc5_utils import (derive_key_from_passphrase, validate_passphrase,
                               validate_file_for_encryption, validate_file_for_decryption,
                               handle_encryption_error, handle_decryption_error)
from ..rc5_cbc import encrypt_file_stream, decrypt_file_stream
router = APIRouter()
@router.post("/encrypt")
async def encrypt(
    file: UploadFile = File(...),
    passfile: UploadFile = File(...)
):
    try:
        validate_passphrase(passfile)
        validate_file_for_encryption(file)
        
        key = await derive_key_from_passphrase(passfile)
        
        filename = f"{file.filename}.enc"
        filename = quote(filename)
        return StreamingResponse(
            encrypt_file_stream(file, key),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise handle_encryption_error(e)
    
    
@router.post("/decrypt")
async def decrypt(
    encrypted_file: UploadFile = File(...),
    passfile: UploadFile = File(...)
):
    try:
        validate_passphrase(passfile)
        validate_file_for_decryption(encrypted_file)
        
        key = await derive_key_from_passphrase(passfile)
        
        filename = f"{encrypted_file.filename.replace('.enc', '')}"
        filename = quote(filename)
        return StreamingResponse(
            decrypt_file_stream(encrypted_file, key),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
        )
    except Exception as e:
        raise handle_decryption_error(e)
    except HTTPException:
        raise