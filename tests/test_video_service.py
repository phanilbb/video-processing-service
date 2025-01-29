import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from flask import Flask

from app.service.video_service import VideoService
from app.exceptions.video_exceptions import (
    VideoValidationException,
    VideoProcessingException,
    VideoNotFoundException
)
import tempfile
import os
from app.extension import db
from app.videos.models import Video


class TestVideoService(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory DB for testing
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(self.app)

        with self.app.app_context():
            db.create_all()  # Create tables
            # Add a sample video to the database
            video = Video(
                id=1,  # Ensure this matches the video_id in your test
                filename="test_video.mp4",
                size=12345,
                duration=60,
                file_path="/mock/path/test_video.mp4"
            )
            db.session.add(video)
            db.session.commit()

        self.video_service = VideoService()

    @patch("app.service.video_service.VideoProcessor")
    @patch("app.service.video_service.VideoValidator")
    @patch("app.service.video_service.db.session")
    def test_upload_video_success(self, mock_db_session, MockVideoValidator, MockVideoProcessor):
        # Mocking
        mock_file = MagicMock()
        mock_file.filename = "test_video.mp4"

        mock_video = MagicMock()
        mock_video.id = 1
        mock_video.filename = mock_file.filename

        MockVideoProcessor.return_value.process_upload.return_value = mock_video
        MockVideoValidator.return_value.validate.return_value = None

        # Test
        response = self.video_service.upload_video(mock_file)

        # Assert
        self.assertEqual(response["message"], "Video uploaded successfully")
        self.assertEqual(response["video_id"], mock_video.id)
        mock_db_session.add.assert_called_once_with(mock_video)
        mock_db_session.commit.assert_called_once()

    @patch("app.service.video_service.VideoProcessor")
    def test_upload_video_processing_failure(self, MockVideoProcessor):
        # Mocking
        mock_file = MagicMock()
        mock_file.filename = "test_video.mp4"
        MockVideoProcessor.return_value.process_upload.side_effect = Exception("Processing error")

        # Test & Assert
        with self.assertRaises(VideoProcessingException):
            self.video_service.upload_video(mock_file)

    @patch("os.remove")
    @patch("app.service.video_service.VideoValidator")
    def test_validate_video_failure(self, MockVideoValidator, mock_os_remove):
        # Arrange: Create a temporary file to simulate the video file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name  # Path to the temp file

        mock_video = MagicMock()
        mock_video.filename = "test_video.mp4"
        mock_video.file_path = temp_file_path

        MockVideoValidator.return_value.validate.return_value = "Validation error"

        # Act & Assert
        with self.assertRaises(VideoValidationException):
            self.video_service._validate_video(mock_video)

        # Verify: Ensure os.remove was called with the correct file path
        mock_os_remove.assert_called_once_with(temp_file_path)

        # Cleanup: Remove the temporary file if it still exists
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    @patch("app.service.video_service.Video")
    def test_get_video_success(self, MockVideo):
        # Mocking
        mock_video = MagicMock()
        mock_video.id = 1
        mock_video.filename = "test_video.mp4"
        MockVideo.query.get.return_value = mock_video

        # Test
        response = self.video_service.get_video(mock_video.id)

        # Assert
        self.assertEqual(response["id"], mock_video.id)
        self.assertEqual(response["filename"], mock_video.filename)

    @patch("app.service.video_service.Video")
    def test_get_video_not_found(self, MockVideo):
        # Mocking
        MockVideo.query.get.return_value = None

        # Test & Assert
        with self.assertRaises(VideoNotFoundException):
            self.video_service.get_video(999)

    @patch("app.service.video_service.VideoProcessor")
    def test_trim_video_success(self, MockVideoProcessor):
        # Mocking
        mock_video = MagicMock()
        mock_video.id = 1

        trimmed_video = MagicMock()
        trimmed_video.id = 2

        MockVideoProcessor.return_value.trim_video_file.return_value = trimmed_video

        with patch.object(self.video_service, '_get_video_from_db', return_value=mock_video):
            with patch.object(self.video_service, '_save_video_to_db') as mock_save:
                response = self.video_service.trim_video(mock_video.id, 0, 10)

                # Assert
                self.assertEqual(response["message"], "Video trimmed successfully")
                self.assertEqual(response["video_id"], trimmed_video.id)
                mock_save.assert_called_once_with(trimmed_video)

    @patch("app.service.video_service.VideoProcessor")
    def test_merge_videos_success(self, MockVideoProcessor):
        # Mocking
        mock_video_1 = MagicMock(id=1)
        mock_video_2 = MagicMock(id=2)
        merged_video = MagicMock(id=3)

        MockVideoProcessor.return_value.merge_video_files.return_value = merged_video

        with patch.object(self.video_service, '_get_videos_from_db', return_value=[mock_video_1, mock_video_2]):
            with patch.object(self.video_service, '_save_video_to_db') as mock_save:
                response = self.video_service.merge_videos([1, 2])

                # Assert
                self.assertEqual(response["message"], "Videos merged successfully")
                self.assertEqual(response["video_id"], merged_video.id)
                mock_save.assert_called_once_with(merged_video)

    @patch("app.service.video_service.VideoShare")
    @patch("app.service.video_service.url_for")
    def test_generate_shareable_link_success(self, mock_url_for, MockVideoShare):
        with self.app.app_context():  # Set up the application context
            # Mocking
            mock_video_id = 1
            mock_token = "mock_token"
            mock_expiry_time = datetime.utcnow() + timedelta(hours=24)

            mock_url_for.return_value = "http://mocksharelink.com"

            # Mock methods in VideoService
            with patch.object(self.video_service, '_generate_token', return_value=mock_token):
                with patch.object(self.video_service, '_save_shareable_link') as mock_save_link:
                    # Call the method under test
                    response = self.video_service.generate_shareable_link(mock_video_id)

                    # Assert
                    self.assertEqual(response["share_url"], "http://mocksharelink.com")
                    self.assertIn("expiry_time", response)  # Validate expiry time exists in response
                    mock_save_link.assert_called_once_with(mock_video_id, mock_token, mock_save_link.call_args[0][
                        2])  # Assert correct args passed to save_shareable_link


if __name__ == "__main__":
    unittest.main()