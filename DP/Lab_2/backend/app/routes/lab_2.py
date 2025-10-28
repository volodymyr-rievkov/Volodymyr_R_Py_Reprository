from fastapi import APIRouter, Request, File, UploadFile, HTTPException, Form
from ..utils.md5_utils import extract_provided_hash, md5_from_string, md5_from_file, calculate_md5

router = APIRouter()

@router.post("/hash-string")
async def hash_string(request: Request):
    data = await request.json()
    input_text = data.get("input", "")
    hash_value = md5_from_string(input_text)
    return {"md5_hash": hash_value.upper()}


@router.post("/hash-file")
async def hash_file(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    hash_value = await md5_from_file(file)
    return {"md5_hash": hash_value.upper()}


@router.post("/verify-hash")
async def verify(
    input_text: str = Form(None),
    file: UploadFile = File(None),
    md5_hash: str = Form(None),
    hash_file: UploadFile = File(None)
):
    if input_text is None and file is None:
        raise HTTPException(status_code=400, detail="Provide text or file to check")


    if not (md5_hash or hash_file):
        raise HTTPException(status_code=400, detail="Provide MD5 hash as text or file")

    provided_hash = await extract_provided_hash(md5_hash, hash_file)
    source = file or input_text

    try:
        calculated_hash = await calculate_md5(source)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating hash: {str(e)}")

    is_valid = calculated_hash.lower() == provided_hash.lower()

    return {
        "provided_hash": provided_hash.upper(),
        "calculated_hash": calculated_hash.upper(),
        "is_valid": is_valid
    }
