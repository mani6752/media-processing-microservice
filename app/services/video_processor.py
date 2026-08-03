import ffmpeg


class VideoProcessor:

    @staticmethod
    def create_thumbnail(input_path: str, output_path: str):
        try:
            (
                ffmpeg
                .input(input_path, ss=1)
                .output(output_path, vframes=1)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error as e:
            print("========== FFMPEG ERROR ==========")
            print(e.stderr.decode("utf-8"))
            raise

    @staticmethod
    def convert_to_mp4(input_path: str, output_path: str):
        try:
            (
                ffmpeg
                .input(input_path)
                .output(
                    output_path,
                    vcodec="libx264",
                    acodec="aac",
                    preset="fast"
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error as e:
            print("========== FFMPEG ERROR ==========")
            print(e.stderr.decode("utf-8"))
            raise
        