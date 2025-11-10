from PIL import Image
import imagehash
from io import BytesIO

def phash_from_bytes(b: bytes) -> str:
    img = Image.open(BytesIO(b)).convert("RGB")
    return str(imagehash.phash(img))
