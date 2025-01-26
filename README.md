# Video Processing API

This is a Flask-based API designed for video uploading, trimming, merging, and sharing functionality. It allows users to upload videos, trim them, merge multiple videos, and share them through a token-based system.

## Project Structure

```commandline
video-processing-service/
│── app/
│   │── config/
│   │   └── __init__.py
│   │── exceptions/
│   │   ├── __init__.py
│   │   └── video_exceptions.py
│   │── logging/
│   │   └── __init__.py
│   │── routes/
│   │   ├── __init__.py
│   │   └── video_routes.py
│   │── service/
│   │   ├── processor/
│   │   │   ├── __init__.py
│   │   │   └── video_processor.py
│   │   ├── validator/
│   │   │   ├── __init__.py
│   │   │   └── video_validator.py
│   │   ├── __init__.py
│   │   └── video_service.py
│   │── utils/
│   │   ├── __init__.py
│   │   └── file_utils.py
│   │── videos/
│   │   ├── __init__.py
│   │   └── models.py
│── app.log
│── app.py
│── authentication.py
│── constants.py
│── extension.py
│── tests/
│── migrations/
│── README.md
```
