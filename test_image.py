from PIL import Image
from io import BytesIO
from app.services.image_service import resize_image, create_thumbnail, crop_image, ImageProcessingError
# make a fake test image
img = Image.new("RGB", (1600, 900), color=(200, 50, 50))
buf = BytesIO()
img.save(buf, format="JPEG")
test_bytes = buf.getvalue()

resized = resize_image(test_bytes)
thumb = create_thumbnail(test_bytes)
cropped = crop_image(test_bytes, target_ratio=1.0)  # square

print(f"resized: {len(resized)} bytes")
print(f"thumbnail: {len(thumb)} bytes")
print(f"cropped: {len(cropped)} bytes")

# verify square crop worked
cropped_img = Image.open(BytesIO(cropped))
print(f"cropped dimensions: {cropped_img.size}")  # should be square, e.g. (900, 900)

# test error handling
try:
    resize_image(b"not an image")
except ImageProcessingError as e:
    print(f"correctly caught bad input: {e}")