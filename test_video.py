from app.services.video_processor import VideoProcessor

VideoProcessor.create_thumbnail(
    "media/input/sample.mp4",
    "media/output/thumbnail.jpg"
)

VideoProcessor.convert_to_mp4(
    "media/input/sample.mp4",
    "media/output/output.mp4"
)

print("✅ Video processing completed successfully!")
