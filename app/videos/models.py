from app.extension import db  # Import the SQLAlchemy instance
from datetime import datetime

class Video(db.Model):
    __tablename__ = 'videos'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    size = db.Column(db.Integer, nullable=False)  # File size in bytes
    duration = db.Column(db.Integer, nullable=False)  # Duration in seconds
    file_path = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Video {self.filename}>'

class VideoShare(db.Model):
    __tablename__ = 'video_shares'
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    token = db.Column(db.String(64), nullable=False, unique=True)
    expiry_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    video = db.relationship('Video', backref=db.backref('shares', lazy=True))

