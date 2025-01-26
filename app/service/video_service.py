import logging
import os
from app.constants import SHARE_DURATION
from app.exceptions.video_exceptions import VideoValidationException, VideoProcessingException, VideoNotFoundException
from app.extension import db
from app.service.processor.video_processor import VideoProcessor
from app.service.validator.video_validator import VideoValidator
from app.videos.models import Video, VideoShare
import hashlib
from datetime import datetime, timedelta
from flask import url_for


class VideoService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def upload_video(self, file):
        """Upload a new video"""
        try:
            video = self._process_video_upload(file)
            self._validate_video(video)
            self._save_video_to_db(video)
        except VideoProcessingException as e:
            raise e
        except VideoValidationException as e:
            raise e
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise VideoProcessingException(str(e))

        return {"message": "Video uploaded successfully", "video_id": video.id}

    def _process_video_upload(self, file):
        """Process the video file"""
        self.logger.info(f"Processing video for file: {file.filename}")
        try:
            video_processor = VideoProcessor()
            return video_processor.process_upload(file)
        except Exception as e:
            self.logger.error(f"Processing error: {str(e)}")
            raise VideoProcessingException(str(e))

    def _validate_video(self, video):
        """Validate the uploaded video"""
        self.logger.info(f"Validating video for file: {video.filename}")
        validator = VideoValidator(video)
        validation_err = validator.validate()
        if validation_err:
            self.logger.error(f"Validation error: {validation_err}")
            os.remove(video.file_path)
            raise VideoValidationException(validation_err)

    def _save_video_to_db(self, video):
        """Save the video record to the database"""
        try:
            self.logger.info(f"Saving video for file: {video.filename}")
            db.session.add(video)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Database error: {str(e)}")
            raise VideoProcessingException(f"Database error: {str(e)}")

    def get_video(self, video_id):
        """Retrieve video details by ID"""
        video = self._get_video_from_db(video_id)
        return {
            "id": video.id,
            "filename": video.filename,
            "size": video.size,
            "duration": video.duration,
            "file_path": video.file_path
        }

    def _get_video_from_db(self, video_id):
        """Retrieve video from DB by ID"""
        self.logger.info(f"Fetching video for ID: {video_id}")
        video = Video.query.get(video_id)
        if not video:
            self.logger.error(f"Video not found for ID: {video_id}")
            raise VideoNotFoundException(f"Video not found for ID: {video_id}")
        return video

    def trim_video(self, video_id, start, end):
        """Trim the video to the given start and end times"""
        video = self._get_video_from_db(video_id)
        trimmed_video = self._process_video_trim(video, start, end)
        self._save_video_to_db(trimmed_video)
        return {"message": "Video trimmed successfully", "video_id": trimmed_video.id}

    def _process_video_trim(self, video, start, end):
        """Trim the video file"""
        try:
            self.logger.info(f"Processing video for trimming: {video.id}")
            video_processor = VideoProcessor()
            return video_processor.trim_video_file(video, start, end)
        except Exception as e:
            self.logger.error(f"Processing error while trimming: {str(e)}")
            raise VideoProcessingException(str(e))

    def merge_videos(self, video_ids):
        """Merge multiple videos into one"""
        self._validate_video_ids(video_ids)
        if len(video_ids) == 1:
            raise VideoValidationException("At least 2 videos are required to merge")

        videos = self._get_videos_from_db(video_ids)
        merged_video = self._process_video_merge(videos)
        self._save_video_to_db(merged_video)
        return {"message": "Videos merged successfully", "video_id": merged_video.id}

    def _validate_video_ids(self, video_ids):
        """Validate video IDs for merging"""
        video_validator = VideoValidator(None)
        validation_err = video_validator.validate_video_ids(video_ids)
        if validation_err:
            self.logger.error(f"Validation error: {validation_err}")
            raise VideoValidationException(validation_err)

    def _get_videos_from_db(self, video_ids):
        """Retrieve multiple videos from DB by IDs"""
        videos = Video.query.filter(Video.id.in_(video_ids)).all()
        if len(video_ids) != len(videos):
            found_video_ids = [video.id for video in videos]
            not_found_ids = [video_id for video_id in video_ids if video_id not in found_video_ids]
            self.logger.error(f"Video not found Ids: {str(not_found_ids)}")
            raise VideoNotFoundException(f"Video not found Ids: {str(not_found_ids)}")
        return videos

    def _process_video_merge(self, videos):
        """Merge video files"""
        try:
            self.logger.info(f"Processing videos for merging: {[video.id for video in videos]}")
            video_processor = VideoProcessor()
            return video_processor.merge_video_files(videos)
        except Exception as e:
            self.logger.error(f"Processing error while merging: {str(e)}")
            raise VideoProcessingException(str(e))

    def generate_shareable_link(self, video_id, expiry_duration=SHARE_DURATION):
        """Generate a time-expiring shareable link for a video."""
        self._get_video_from_db(video_id)
        current_time = datetime.utcnow()
        expiry_time = current_time + timedelta(hours=expiry_duration)

        token = self._generate_token(video_id, current_time)
        self._save_shareable_link(video_id, token, expiry_time)

        share_url = url_for('video_routes.get_video_from_shared_token', token=token, _external=True)
        return {"share_url": share_url, "expiry_time": expiry_time}

    def _generate_token(self, video_id, current_time):
        """Generate a unique token"""
        return hashlib.sha256(f"{video_id}-{current_time.timestamp()}".encode()).hexdigest()

    def _save_shareable_link(self, video_id, token, expiry_time):
        """Save the shareable link in the database"""
        try:
            self.logger.info(f"Saving shareable video for video: {video_id} with token {token}")
            video_share = VideoShare(video_id=video_id, token=token, expiry_time=expiry_time)
            db.session.add(video_share)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Database error: {str(e)}")
            raise VideoProcessingException(f"Database error: {str(e)}")

    def get_shared_video_from_token(self, token):
        """Handle access to shareable video links."""
        video_share = self._get_video_share_by_token(token)
        self._check_link_expiry(video_share)
        video = Video.query.get(video_share.video_id)
        return {
            "id": video.id,
            "filename": video.filename,
            "size": video.size,
            "duration": video.duration,
            "file_path": video.file_path
        }

    def _get_video_share_by_token(self, token):
        """Retrieve the VideoShare object from the database"""
        video_share = VideoShare.query.filter_by(token=token).first()
        if not video_share:
            raise VideoNotFoundException(f"No shared video found with token {token}")
        return video_share

    def _check_link_expiry(self, video_share):
        """Check if the shareable link has expired"""
        if video_share.expiry_time < datetime.utcnow():
            raise VideoValidationException("The shared URL has expired")
