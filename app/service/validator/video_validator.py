from app.constants import MIN_SIZE, MAX_SIZE, MIN_DURATION, MAX_DURATION  # Import constants


class VideoValidator:
    def __init__(self, video, min_size=MIN_SIZE, max_size=MAX_SIZE, min_duration=MIN_DURATION,
                 max_duration=MAX_DURATION):
        self.video = video
        self.min_size = min_size
        self.max_size = max_size
        self.min_duration = min_duration
        self.max_duration = max_duration

    def validate_size(self, file_size):
        """Validate video file size"""
        if file_size > self.max_size:
            return f"File size exceeds the maximum limit of {self.max_size / (1024 * 1024)} MB."
        if file_size < self.min_size:
            return f"File size is below the minimum limit of {self.min_size / (1024 * 1024)} MB."
        return None

    def validate_duration(self, duration):
        """Validate video file duration"""
        if duration < self.min_duration:
            return f"Video duration is too short. Minimum duration is {self.min_duration} seconds."
        if duration > self.max_duration:
            return f"Video duration is too long. Maximum duration is {self.max_duration} seconds."
        return None

    def validate(self):
        # Check video size
        size_error = self.validate_size(self.video.size)
        if size_error:
            return size_error

        # Validate video duration directly from memory
        duration_error = self.validate_duration(self.video.duration)
        if duration_error:
            return duration_error

        return None

    def validate_video_ids(self, video_ids):
        """Ensure video_ids is a list of integers."""
        if not isinstance(video_ids, list):
            return "video_ids must be a list."

        if not all(isinstance(id, int) for id in video_ids):
            return "All items in video_ids must be integers."

        return None
