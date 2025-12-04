from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from ..dsa import sign_stream, verify_stream
from ..utils.dsa_utils import generate_dsa_keys

router = APIRouter()

@router.post("/generate_keys")
def generate_keys(bits: int = 2048):
    try:
        private_key, public_key = generate_dsa_keys(bits)
        return {
            "private_key": private_key,
            "public_key": public_key
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Key generation failed: {str(e)}")


@router.post("/sign")
async def sign_file(
    data_file: UploadFile = File(...),
    private_key_file: UploadFile = File(...)
):
    try:
        private_key_pem = (await private_key_file.read()).decode()

        signature = sign_stream(data_file.file, private_key_pem)

        return Response(
            content=signature,
            media_type="application/octet-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Sign failed: {str(e)}")


@router.post("/verify")
async def verify_file(
    data_file: UploadFile = File(...),
    signature_file: UploadFile = File(...),
    public_key_file: UploadFile = File(...)
):
    try:
        public_key_pem = (await public_key_file.read()).decode()
        signature = await signature_file.read() 

        valid = verify_stream(data_file.file, public_key_pem, signature)

        return {"valid": valid}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Verify failed: {str(e)}")
