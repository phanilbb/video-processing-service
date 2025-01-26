import logging
import os
import uuid

from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip

from app.config import Config
from app.videos.models import Video


class VideoProcessor:
    def __init__(self, video_dir=None):
        self.logger = logging.getLogger(__name__)
        self.video_dir = video_dir or Config.VIDEO_DIR
        self._ensure_video_directory()

    def _ensure_video_directory(self):
        """Ensure that the video directory exists."""
        if not os.path.exists(self.video_dir):
            os.makedirs(self.video_dir)

    def process_upload(self, file):
        """Process the uploaded video file and save it."""
        unique_filename = self._generate_unique_filename(file.filename)
        file_path = os.path.join(self.video_dir, unique_filename)
        self._save_video_file(file, file_path)

        video_clip = VideoFileClip(file_path)
        return self._create_video_object(unique_filename, file_path, video_clip)

    def _generate_unique_filename(self, original_filename):
        """Generate a unique filename using UUID."""
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        self.logger.info(f"Generated unique filename: {unique_filename} for original file: {original_filename}")
        return unique_filename

    def _save_video_file(self, file, file_path):
        """Save the uploaded video file to disk."""
        file.save(file_path)
        self.logger.info(f"File {file.filename} saved at path {file_path}")

    def _create_video_object(self, filename, file_path, video_clip):
        """Create a Video object for the uploaded video."""
        return Video(
            filename=filename,
            size=os.path.getsize(file_path),
            duration=video_clip.duration,
            file_path=file_path
        )

    def trim_video_file(self, video, start, end):
        """Trim the video from the start to the end time."""
        clip = self._get_video_clip(video.file_path).subclipped(start, end)
        unique_filename = self._generate_unique_filename(video.filename)
        new_file_path = os.path.join(self.video_dir, unique_filename)
        self._save_trimmed_video(clip, new_file_path)

        return self._create_video_object(unique_filename, new_file_path, clip)

    def _get_video_clip(self, file_path):
        """Load and return a video clip from the given file path."""
        return VideoFileClip(file_path)

    def _save_trimmed_video(self, clip, new_file_path):
        """Save the trimmed video file."""
        clip.write_videofile(new_file_path)
        self.logger.info(f"Trimmed video saved at path {new_file_path}")

    def merge_video_files(self, videos):
        """Merge multiple video files into a single file."""
        clips = self._load_video_clips(videos)
        final_clip = concatenate_videoclips(clips)
        unique_filename = self._generate_unique_filename(videos[0].filename)
        merged_file_path = os.path.join(self.video_dir, unique_filename)
        self._save_merged_video(final_clip, merged_file_path)

        return self._create_video_object(unique_filename, merged_file_path, final_clip)

    def _load_video_clips(self, videos):
        """Load and return the video clips for the given videos."""
        return [VideoFileClip(video.file_path) for video in videos]

    def _save_merged_video(self, final_clip, merged_file_path):
        """Save the merged video file."""
        final_clip.write_videofile(merged_file_path)
        self.logger.info(f"Merged video saved at path {merged_file_path}")
