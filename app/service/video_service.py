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
        self.logger.info("fetch video for ID : {}".format(video_id))
        video = Video.query.get(video_id)
        if not video:
            # Raise exception if video not found
            self.logger.error("video not found for ID : {}".format(video_id))
            raise VideoNotFoundException("video not found for ID : {}".format(video_id))

        # Prepare video data to return
        self.logger.info("video found for ID : {}".format(video_id))
        return {
            "id": video.id,
            "filename": video.filename,
            "size": video.size,
            "duration": video.duration,
            "file_path": video.file_path
        }

    def trim_video(self, video_id, start, end):
        """Trim the video to the given start and end times"""
        # Retrieve the video record from the database
        video = self.get_video(video_id)
        if not video:
            self.logger.error("video not found for ID : {}".format(video_id))
            raise VideoNotFoundException("video not found for ID : {}".format(video_id))

        # video trimming process
        # process the video to save in DB
        try:
            self.logger.info("processing video for trimming : {}".format(video_id))
            video_processor = VideoProcessor()
            trimmed_video = video_processor.trim_video_file(video, start, end)
        except Exception as e:
            self.logger.error("Processing error while trimming : {}".format(str(e)))
            raise VideoProcessingException(str(e))

        # Save the trimmed video to the database
        try:
            # Add the video record to the database
            self.logger.info("saving trimmed video for file : {}".format(trimmed_video.filename))
            db.session.add(trimmed_video)
            db.session.commit()
        except Exception as e:
            # Handle specific database issues (e.g., duplicate entries)
            db.session.rollback()  # Rollback the transaction to maintain data integrity
            self.logger.error("Database error : {}".format(str(e)))
            raise VideoProcessingException(f"Database error: {str(e)}")

        return {"message": "Video trimmed successfully", "video_id": trimmed_video.id}

    def merge_videos(self, video_ids):
        """Merge multiple videos into one"""

        video_validator = VideoValidator(None)
        validation_err = video_validator.validate_video_ids(video_ids)
        if validation_err:
            self.logger.error("Validation error : {}".format(validation_err))
            raise VideoValidationException(validation_err)

        if len(video_ids) == 1:
            self.logger.error("At least 2 videos are required to merge")
            raise VideoValidationException("At least 2 videos are required to merge")

        self.logger.error("Merging videos for Ids : {}".format(str(video_ids)))

        # Retrieve the video records from the database
        videos = Video.query.filter(Video.id.in_(video_ids)).all()

        if len(video_ids) != len(videos):
            found_video_ids = [each_video.id for each_video in videos]
            # Remove the found ids from video_ids
            not_found_ids = [video_id for video_id in video_ids if video_id not in found_video_ids]
            self.logger.error("Video not found Ids : {}".format(str(not_found_ids)))
            raise VideoNotFoundException("Video not found Ids : {}".format(str(not_found_ids)))

        # Perform the video merging process
        try:
            self.logger.info("processing videos for merging : {}".format(video_ids))
            video_processor = VideoProcessor()
            merged_video = video_processor.merge_video_files(videos)
        except Exception as e:
            self.logger.error("Processing error while merging : {}".format(str(e)))
            raise VideoProcessingException(str(e))

        # Save the merged video to the database
        try:
            # Add the video record to the database
            self.logger.info("saving trimmed video for file : {}".format(merged_video.filename))
            db.session.add(merged_video)
            db.session.commit()
        except Exception as e:
            db.session.rollback()  # Rollback the transaction to maintain data integrity
            self.logger.error("Database error : {}".format(str(e)))
            raise VideoProcessingException(f"Database error: {str(e)}")

        return {"message": "Videos merged successfully", "video_id": merged_video.id}
