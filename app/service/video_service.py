import logging
import os

from app.exceptions.video_exceptions import VideoValidationException, VideoProcessingException, VideoNotFoundException
from app.extension import db
from app.service.processor.video_processor import VideoProcessor
from app.service.validator.video_validator import VideoValidator
from app.videos.models import Video


class VideoService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def upload_video(self, file):
        """Upload a new video"""
        # process the video to save in DB
        try:
            self.logger.info("processing video for file : {}".format(file.filename))
            video_processor = VideoProcessor()
            video = video_processor.process_upload(file)
        except Exception as e:
            self.logger.error("Processing error : {}".format(str(e)))
            raise VideoProcessingException(str(e))

        # validate the video
        self.logger.info("validating video for file : {}".format(file.filename))
        validator = VideoValidator(video)
        validation_err = validator.validate()
        if validation_err:
            self.logger.error("Validation error : {}".format(validation_err))
            os.remove(video.file_path)
            raise VideoValidationException(validation_err)

        # Add the video record to the database
        try:
            # Add the video record to the database
            self.logger.info("saving video for file : {}".format(file.filename))
            db.session.add(video)
            db.session.commit()
        except Exception as e:
            # Handle specific database issues (e.g., duplicate entries)
            db.session.rollback()  # Rollback the transaction to maintain data integrity
            self.logger.error("Database error : {}".format(validation_err))
            raise VideoProcessingException(f"Database error: {str(e)}")

        self.logger.info("Video uploaded successfully for file : {}".format(file.filename))
        return {
            "message": "Video uploaded successfully",
            "video_id": video.id,
        }

    def get_video(self, video_id):
        """Retrieve video details by ID"""
        # Retrieve the video record from the database
        video = Video.query.get(video_id)
        if not video:
            # Raise exception if video not found
            raise VideoNotFoundException(video_id)

        # Prepare video data to return
        return {
            "id": video.id,
            "filename": video.filename,
            "size": video.size,
            "duration": video.duration,
            "file_path": video.file_path
        }
