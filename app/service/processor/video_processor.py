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
        if not os.path.exists(self.video_dir):
            os.makedirs(self.video_dir)

    def process_upload(self, file):
        """Process the uploaded video file and save it."""
        file_extension = os.path.splitext(file.filename)[1]  # Extract file extension
        unique_filename = f"{uuid.uuid4()}{file_extension}"  # Generate UUID-based filename

        self.logger.info("Unique filename {} for actual file {}".format(unique_filename, file.filename))
        file_path = os.path.join(self.video_dir, unique_filename)
        file.save(file_path)
        self.logger.info("file {} saved in path {}".format(unique_filename, file_path))

        # Create a VideoFileClip to get duration and other properties
        video_clip = VideoFileClip(file_path)

        # Create a Video object and save video details in the database
        video = Video(
            filename=unique_filename,
            size=os.path.getsize(file_path),
            duration=video_clip.duration,
            file_path=file_path
        )
        return video

    def trim_video_file(self, video, start, end):
        """Trim the video from the start to the end time."""
        clip = VideoFileClip(video['file_path']).subclipped(start, end)
        file_extension = os.path.splitext(video['file_path'])[1]  # Extract file extension
        unique_filename = f"{uuid.uuid4()}{file_extension}"  # Generate UUID-based filename
        new_file_path = os.path.join(self.video_dir, unique_filename)
        clip.write_videofile(new_file_path)
        self.logger.info("Original file {} ".format(video['file_path']))
        self.logger.info("Trimmed file {} ".format(new_file_path))

        # Create a new Video object for the trimmed video
        trimmed_video = Video(
            filename=unique_filename,
            size=os.path.getsize(new_file_path),
            duration=clip.duration,
            file_path=new_file_path
        )
        return trimmed_video
