from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from ..utils.md5_utils import md5_from_file, validate_md5_hash

router = APIRouter()

@router.post("/hash")
async def hash_md5(
    data_file: UploadFile = File(...),
    expected_hash: str = Form(None)
):
    if not data_file:
        raise HTTPException(status_code=400, detail="No data file uploaded")

    computed_hash = await md5_from_file(data_file)
    result = {"computed_hash": computed_hash.upper()}
    
    if expected_hash:
        validate_md5_hash(expected_hash)
        is_valid = computed_hash.lower() == expected_hash.lower()
        result["is_valid"] = is_valid
    
    return result