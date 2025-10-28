import re
from fastapi import HTTPException, UploadFile
from ..md5 import MD5

MD5_REGEX = re.compile(r"^[a-fA-F0-9]{32}$")

def validate_md5_hash(md5_hash: str):
    if not md5_hash:
        raise HTTPException(status_code=400, detail="Provided MD5 hash is empty")
    if not MD5_REGEX.fullmatch(md5_hash):
        raise HTTPException(status_code=400, detail="Invalid MD5 hash format")


async def extract_provided_hash(md5_hash: str | None, hash_file: UploadFile | None) -> str:
    if hash_file:
        provided_hash = (await hash_file.read()).decode("utf-8", errors="ignore").strip()
    else:
        provided_hash = (md5_hash or "").strip()

    validate_md5_hash(provided_hash)
    return provided_hash


def md5_from_string(text: str) -> str:
    md = MD5()
    md.update(text)
    return md.hexdigest()


async def md5_from_file(upload_file, chunk_size=1024 * 512):
    md = MD5()
    while chunk := await upload_file.read(chunk_size):
        md.update(chunk)
    await upload_file.close()
    return md.hexdigest()


async def calculate_md5(data):
    if hasattr(data, "read"):
        return await md5_from_file(data)
    elif isinstance(data, str):
        return md5_from_string(data)
    else:
        raise ValueError(f"Unsupported data type for MD5 calculation: {type(data)}")
