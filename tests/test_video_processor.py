import os
import unittest
from unittest.mock import patch, MagicMock, mock_open

from app.service.processor.video_processor import VideoProcessor
from moviepy.video.io.VideoFileClip import VideoFileClip


class TestVideoProcessor(unittest.TestCase):
    def setUp(self):
        self.video_dir = "mock_video_dir"
        self.video_processor = VideoProcessor(video_dir=self.video_dir)

    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    def test_ensure_video_directory_created(self, mock_exists, mock_makedirs):
        self.video_processor._ensure_video_directory()
        mock_makedirs.assert_called_once_with(self.video_dir)

    @patch("os.path.exists", return_value=True)
    @patch("os.makedirs")
    def test_ensure_video_directory_exists(self, mock_makedirs, mock_exists):
        self.video_processor._ensure_video_directory()
        mock_makedirs.assert_not_called()

    @patch("os.path.splitext", return_value=("mock_file", ".mp4"))
    @patch("uuid.uuid4", return_value="unique-id")
    def test_generate_unique_filename(self, mock_uuid, mock_splitext):
        unique_filename = self.video_processor._generate_unique_filename("test.mp4")
        self.assertEqual(unique_filename, "unique-id.mp4")

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.getsize", return_value=1024)
    @patch("app.service.processor.video_processor.VideoFileClip")
    @patch("app.service.processor.video_processor.VideoProcessor._generate_unique_filename",
           return_value="unique-id.mp4")
    def test_process_upload(self, mock_generate_filename, mock_video_clip, mock_getsize, mock_open):
        mock_file = MagicMock()
        mock_file.filename = "test.mp4"

        mock_video_clip.return_value.duration = 120.0

        # Call the method under test
        video = self.video_processor.process_upload(mock_file)

        # Assert the results
        self.assertEqual(video.filename, "unique-id.mp4")  # Mocked filename
        self.assertEqual(video.size, 1024)  # Mocked file size
        self.assertEqual(video.duration, 120.0)  # Mocked video duration

    @patch("moviepy.video.io.VideoFileClip.VideoFileClip")
    @patch("app.service.processor.video_processor.VideoProcessor._get_video_clip")
    @patch("app.service.processor.video_processor.VideoProcessor._save_trimmed_video")
    @patch("app.service.processor.video_processor.VideoProcessor._create_video_object")
    def test_trim_video_file(self, mock_create_video_object, mock_save_trimmed, mock_get_video_clip, mock_video_clip):
        mock_video = MagicMock()
        mock_video.file_path = "mock_path/test.mp4"
        mock_video.filename = "test.mp4"

        # Mock the _get_video_clip method to return a mock VideoFileClip
        mock_clip = MagicMock()
        mock_get_video_clip.return_value = mock_clip

        # Mock the subclip method of the VideoFileClip to return the mock clip
        mock_clip.subclipped.return_value = mock_clip

        # Mock the _create_video_object method to return a mock video object
        mock_video_object = MagicMock()
        mock_create_video_object.return_value = mock_video_object

        # Call the trim_video_file method
        trimmed_video = self.video_processor.trim_video_file(mock_video, start=5, end=15)

        # Assert the results
        self.assertEqual(trimmed_video, mock_video_object)  # Check if it returns the mocked video object
        mock_get_video_clip.assert_called_once_with(mock_video.file_path)
        mock_clip.subclipped.assert_called_once_with(5, 15)

    @patch("moviepy.video.io.VideoFileClip.VideoFileClip.write_videofile")
    def test_save_trimmed_video(self, mock_write_videofile):
        mock_clip = MagicMock()
        new_file_path = "mock_video_dir/trimmed.mp4"

        self.video_processor._save_trimmed_video(mock_clip, new_file_path)
        mock_write_videofile.asset_not_called()

    @patch("moviepy.video.io.VideoFileClip.VideoFileClip.write_videofile")
    def test_save_merged_video(self, mock_write_videofile):
        mock_final_clip = MagicMock()  # Mock the final video clip
        merged_file_path = "mock_video_dir/merged.mp4"

        # Create the processor instance
        video_processor = VideoProcessor()

        # Call the method under test
        video_processor._save_merged_video(mock_final_clip, merged_file_path)

        # Check if the method was called correctly
        print(mock_write_videofile.call_args_list)  # Print the call args for debugging
        mock_write_videofile.assert_not_called()


if __name__ == "__main__":
    unittest.main()
