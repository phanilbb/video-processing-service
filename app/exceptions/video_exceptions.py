# app/exceptions.py
class VideoValidationException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class VideoProcessingException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class VideoNotFoundException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
