from app.extension import db  # Import the SQLAlchemy instance


class Video(db.Model):
    __tablename__ = 'videos'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    size = db.Column(db.Integer, nullable=False)  # File size in bytes
    duration = db.Column(db.Integer, nullable=False)  # Duration in seconds
    file_path = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Video {self.filename}>'
