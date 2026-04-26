import base64
import hashlib
import uuid
from io import BytesIO
from django.core.files.base import ContentFile


def decode_base64_image(image_data):
    if not image_data or ';base64,' not in image_data:
        raise ValueError('Rasm base64 formatda kelmadi')
    header, imgstr = image_data.split(';base64,', 1)
    ext = header.split('/')[-1].split(';')[0] or 'png'
    binary = base64.b64decode(imgstr)
    return ContentFile(binary, name=f'face_{uuid.uuid4()}.{ext}'), binary


def face_hash_from_binary(binary):
    """Hackathon uchun yengil demo FaceID hash. Pillow bo'lsa average-hash ishlaydi, bo'lmasa sha256 ishlatiladi."""
    try:
        from PIL import Image
        img = Image.open(BytesIO(binary)).convert('L').resize((8, 8))
        pixels = list(img.getdata())
        avg = sum(pixels) / len(pixels)
        return ''.join('1' if p > avg else '0' for p in pixels)
    except Exception:
        return hashlib.sha256(binary).hexdigest()


def hash_distance(h1, h2):
    if not h1 or not h2:
        return 999
    if len(h1) == len(h2) and set(h1 + h2) <= {'0', '1'}:
        return sum(a != b for a, b in zip(h1, h2))
    return 0 if h1 == h2 else 999


def verify_face(stored_hash, new_hash, threshold=22):
    return hash_distance(stored_hash, new_hash) <= threshold
