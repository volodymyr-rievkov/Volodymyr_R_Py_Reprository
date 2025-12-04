from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from ..utils.rsa_utils import generate_rsa_keys
from ..rsa import encrypt_rsa_stream, decrypt_rsa_stream
from ..rsa_hybrid import encrypt_hybrid_stream, decrypt_hybrid_stream

router = APIRouter()

@router.post("/generate_keys")
def generate_keys(bits: int):
    try:
        private_key, public_key = generate_rsa_keys(bits)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    return {"private_key": private_key, "public_key": public_key}


@router.post("/encrypt")
async def encrypt(
    data_file: UploadFile = File(...),
    public_key_file: UploadFile = File(...),
    hybrid: bool = Query(False)
):
    public_key_pem = (await public_key_file.read()).decode()

    try:
        if hybrid:
            generator = encrypt_hybrid_stream(data_file.file, public_key_pem)
        else:
            generator = encrypt_rsa_stream(data_file.file, public_key_pem)

        return StreamingResponse(generator, media_type="application/octet-stream")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Encryption failed: {str(e)}")


@router.post("/decrypt")
async def decrypt(
    encrypted_file: UploadFile = File(...),
    private_key_file: UploadFile = File(...),
    hybrid: bool = Query(False)
):
    private_key_pem = (await private_key_file.read()).decode()

    try:
        if hybrid:
            generator = decrypt_hybrid_stream(encrypted_file.file, private_key_pem)
        else:
            generator = decrypt_rsa_stream(encrypted_file.file, private_key_pem)

        return StreamingResponse(generator, media_type="application/octet-stream")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Decryption failed: {str(e)}")
