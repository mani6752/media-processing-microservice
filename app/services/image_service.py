from io import BytesIO
from PIL import Image


def resize_image(image_bytes: bytes, max_width: int = 1280, max_height: int = 1280) -> bytes:
    img = Image.open(BytesIO(image_bytes))
    img.thumbnail((max_width, max_height))

    output = BytesIO()
    img_format = img.format or "JPEG"
    img.save(output, format=img_format, optimize=True, quality=80)
    return output.getvalue()


def create_thumbnail(image_bytes: bytes, size: tuple[int, int] = (200, 200)) -> bytes:
    img = Image.open(BytesIO(image_bytes))
    img.thumbnail(size)

    output = BytesIO()
    img_format = img.format or "JPEG"
    img.save(output, format=img_format, optimize=True, quality=70)
    return output.getvalue()
