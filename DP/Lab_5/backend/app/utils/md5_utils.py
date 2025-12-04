import re
from fastapi import HTTPException, UploadFile
from ..md5 import MD5

MD5_REGEX = re.compile(r"^[a-fA-F0-9]{32}$")

CHUNK_SIZE = 1024 * 512

def validate_md5_hash(md5_hash: str):
    if not md5_hash:
        raise HTTPException(status_code=400, detail="Provided MD5 hash is empty")
    if not MD5_REGEX.fullmatch(md5_hash):
        raise HTTPException(status_code=400, detail="Invalid MD5 hash format")


async def md5_from_file(upload_file: UploadFile, chunk_size: int=CHUNK_SIZE, hex: bool=True) -> bytes | str:
    md = MD5()
    while chunk := await upload_file.read(chunk_size):
        md.update(chunk)
    await upload_file.close()
    return md.hexdigest() if hex else md.digest()


def md5_bytes(data: bytes) -> bytes:
    md = MD5()
    md.update(data)
    return md.digest()
