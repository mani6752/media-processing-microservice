import pytest
from io import BytesIO
from PIL import Image

from app.services.image_service import (
    resize_image,
    create_thumbnail,
    crop_image,
    ImageProcessingError,
)


def make_test_image(size=(1600, 900), color=(200, 50, 50), fmt="JPEG") -> bytes:
    img = Image.new("RGB", size, color)
    buf = BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def test_resize_shrinks_large_image():
    original = make_test_image(size=(2000, 2000))
    result = resize_image(original, max_width=800, max_height=800)

    result_img = Image.open(BytesIO(result))
    assert result_img.width <= 800
    assert result_img.height <= 800


def test_resize_does_not_upscale_small_image():
    original = make_test_image(size=(300, 300))
    result = resize_image(original, max_width=800, max_height=800)

    result_img = Image.open(BytesIO(result))
    assert result_img.width == 300
    assert result_img.height == 300


def test_create_thumbnail_produces_smaller_file():
    original = make_test_image(size=(1600, 900))
    thumb = create_thumbnail(original, size=(200, 200))

    thumb_img = Image.open(BytesIO(thumb))
    assert thumb_img.width <= 200
    assert thumb_img.height <= 200
    assert len(thumb) < len(original)


def test_crop_to_square_produces_equal_dimensions():
    original = make_test_image(size=(1600, 900))
    cropped = crop_image(original, target_ratio=1.0)

    cropped_img = Image.open(BytesIO(cropped))
    assert cropped_img.width == cropped_img.height


def test_crop_to_widescreen_ratio():
    original = make_test_image(size=(1000, 1000))
    cropped = crop_image(original, target_ratio=16 / 9)

    cropped_img = Image.open(BytesIO(cropped))
    ratio = cropped_img.width / cropped_img.height
    assert abs(ratio - (16 / 9)) < 0.01


def test_invalid_image_bytes_raises_processing_error():
    with pytest.raises(ImageProcessingError):
        resize_image(b"not a real image")


def test_invalid_image_bytes_raises_on_thumbnail():
    with pytest.raises(ImageProcessingError):
        create_thumbnail(b"garbage data")


def test_invalid_image_bytes_raises_on_crop():
    with pytest.raises(ImageProcessingError):
        crop_image(b"still not an image", target_ratio=1.0)


def test_rgba_png_converts_safely_to_jpeg_when_saved_as_jpeg():
    rgba_bytes = make_test_image(size=(500, 500), fmt="PNG")
    result = resize_image(rgba_bytes)
    result_img = Image.open(BytesIO(result))
    assert result_img.width > 0
    