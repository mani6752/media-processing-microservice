from io import BytesIO
from PIL import Image, ImageOps, UnidentifiedImageError


class ImageProcessingError(Exception):
    """Raised when an image cannot be loaded or processed."""


def _load_image(image_bytes: bytes) -> Image.Image:
    """
    Load image bytes into a Pillow Image, fixing EXIF-based rotation
    (common with phone camera uploads) and validating it's a real image.
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        img.load()  # forces Pillow to fully read the file now, catching truncated/corrupt data early
    except (UnidentifiedImageError, OSError) as e:
        raise ImageProcessingError(f"Invalid or corrupted image: {e}") from e

    return ImageOps.exif_transpose(img)


def resize_image(image_bytes: bytes, max_width: int = 1280, max_height: int = 1280) -> bytes:
    img = _load_image(image_bytes)
    img.thumbnail((max_width, max_height))

    output = BytesIO()
    img_format = img.format or "JPEG"

    if img_format.upper() == "JPEG" and img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")

    img.save(output, format=img_format, optimize=True, quality=80)
    return output.getvalue()


def create_thumbnail(image_bytes: bytes, size: tuple[int, int] = (200, 200)) -> bytes:
    img = _load_image(image_bytes)
    img.thumbnail(size)

    output = BytesIO()
    img_format = img.format or "JPEG"

    if img_format.upper() == "JPEG" and img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")

    img.save(output, format=img_format, optimize=True, quality=70)
    return output.getvalue()


def crop_image(image_bytes: bytes, target_ratio: float) -> bytes:
    """
    Center-crop the image to match a target aspect ratio (width / height).
    e.g. target_ratio=1.0 for a square crop, 16/9 for widescreen.
    """
    img = _load_image(image_bytes)
    w, h = img.size
    current_ratio = w / h

    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        box = (left, 0, left + new_w, h)
    else:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        box = (0, top, w, top + new_h)

    cropped = img.crop(box)

    output = BytesIO()
    img_format = img.format or "JPEG"

    if img_format.upper() == "JPEG" and cropped.mode in ("RGBA", "P", "LA"):
        cropped = cropped.convert("RGB")

    cropped.save(output, format=img_format, optimize=True, quality=80)
    return output.getvalue()
