import os
import subprocess
import pytest

from app.services.video_processor import VideoProcessor


@pytest.fixture(scope="module")
def sample_video(tmp_path_factory):
    tmp_dir = tmp_path_factory.mktemp("video_fixtures")
    video_path = tmp_dir / "sample.mp4"

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "testsrc=duration=2:size=320x240:rate=10",
            str(video_path),
        ],
        check=True,
        capture_output=True,
    )

    return str(video_path)


def test_create_thumbnail_produces_nonempty_jpg(sample_video, tmp_path):
    output_path = str(tmp_path / "thumb.jpg")

    VideoProcessor.create_thumbnail(sample_video, output_path)

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_convert_to_mp4_produces_nonempty_output(sample_video, tmp_path):
    output_path = str(tmp_path / "converted.mp4")

    VideoProcessor.convert_to_mp4(sample_video, output_path)

    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0


def test_create_thumbnail_raises_on_invalid_input(tmp_path):
    fake_input = str(tmp_path / "does_not_exist.mp4")
    output_path = str(tmp_path / "thumb.jpg")

    with pytest.raises(Exception):
        VideoProcessor.create_thumbnail(fake_input, output_path)
        