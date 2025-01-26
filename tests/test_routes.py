import io
from unittest.mock import patch

import pytest
from flask import Flask
import os

from app.exceptions.video_exceptions import VideoNotFoundException
from app.routes.video_routes import video_routes
from app.service.video_service import VideoService


@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(video_routes)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


# Test for /video (POST) route
def test_upload(client):
    with patch.object(VideoService, 'upload_video') as mock_upload_video:
        mock_upload_video.return_value = {"message": "Video uploaded successfully"}
        data = {
            'file': (io.BytesIO(b"video data"), 'test_video.mp4')
        }
        headers = {
            'Authorization': 'Bearer ' + os.getenv('API_TOKEN', 'supersecretkey')
        }
        response = client.post('/video', data=data, headers=headers)

        assert response.status_code == 201
        assert response.json == {"message": "Video uploaded successfully"}


def test_upload_invalid_file(client):
    headers = {
        'Authorization': 'Bearer ' + os.getenv('API_TOKEN', 'supersecretkey')
    }
    response = client.post('/video', data={}, headers=headers)
    assert response.status_code == 400
    assert response.json == {"message": "Invalid file"}


# Test for /video/<video_id> (GET) route
def test_get_video(client):
    with patch.object(VideoService, 'get_video') as mock_get_video:
        mock_get_video.return_value = {"video_id": 1, "title": "Test Video"}
        headers = {
            'Authorization': 'Bearer ' + os.getenv('API_TOKEN', 'supersecretkey')
        }
        response = client.get('/video/1', headers=headers)

        assert response.status_code == 200
        assert response.json == {"video_id": 1, "title": "Test Video"}


def test_get_video_not_found(client):
    with patch.object(VideoService, 'get_video') as mock_get_video:
        mock_get_video.side_effect = VideoNotFoundException("Video not found")
        headers = {
            'Authorization': 'Bearer ' + os.getenv('API_TOKEN', 'supersecretkey')
        }
        response = client.get('/video/999', headers=headers)

        assert response.status_code == 404
        assert response.json == {"error": "Video not found"}


# Test for /video/<video_id>/trim (POST) route
def test_trim_video(client):
    with patch.object(VideoService, 'trim_video') as mock_trim_video:
        mock_trim_video.return_value = {"message": "Video trimmed successfully"}
        headers = {
            'Authorization': 'Bearer ' + os.getenv('API_TOKEN', 'supersecretkey')
        }
        response = client.post('/video/1/trim', json={"start": 10, "end": 20}, headers=headers)

        assert response.status_code == 200
        assert response.json == {"message": "Video trimmed successfully"}


def test_trim_video_invalid_params(client):
    headers = {
        'Authorization': 'Bearer ' + os.getenv('API_TOKEN', 'supersecretkey')
    }
    response = client.post('/video/1/trim', json={"start": 10}, headers=headers)

    assert response.status_code == 400
    assert response.json == {"error": "Invalid parameters : 'start' and 'end' are mandatory required fields"}


# Test for /videos/merge (POST) route
def test_merge_videos(client):
    with patch.object(VideoService, 'merge_videos') as mock_merge_videos:
        mock_merge_videos.return_value = {"message": "Videos merged successfully"}
        headers = {
            'Authorization': 'Bearer ' + os.getenv('API_TOKEN', 'supersecretkey')
        }
        response = client.post('/videos/merge', json={"video_ids": [1, 2, 3]}, headers=headers)

        assert response.status_code == 200
        assert response.json == {"message": "Videos merged successfully"}


def test_merge_videos_invalid_params(client):
    headers = {
        'Authorization': 'Bearer ' + os.getenv('API_TOKEN', 'supersecretkey')
    }
    response = client.post('/videos/merge', json={}, headers=headers)

    assert response.status_code == 400
    assert response.json == {"error": "Invalid parameters : 'video_ids' is a mandatory required field"}


# Test for /video/<video_id>/share (POST) route
def test_get_share_link(client):
    with patch.object(VideoService, 'generate_shareable_link') as mock_generate_shareable_link:
        mock_generate_shareable_link.return_value = {"share_link": "http://example.com/share/123"}
        headers = {
            'Authorization': 'Bearer ' + os.getenv('API_TOKEN', 'supersecretkey')
        }
        response = client.post('/video/1/share', headers=headers)

        assert response.status_code == 200
        assert response.json == {"share_link": "http://example.com/share/123"}


def test_get_share_link_video_not_found(client):
    with patch.object(VideoService, 'generate_shareable_link') as mock_generate_shareable_link:
        mock_generate_shareable_link.side_effect = VideoNotFoundException("Video not found")
        headers = {
            'Authorization': 'Bearer ' + os.getenv('API_TOKEN', 'supersecretkey')
        }
        response = client.post('/video/999/share', headers=headers)

        assert response.status_code == 404
        assert response.json == {"error": "Video not found"}


# Test for /video/share/<token> (GET) route
def test_get_video_from_shared_token(client):
    with patch.object(VideoService, 'get_shared_video_from_token') as mock_get_shared_video_from_token:
        mock_get_shared_video_from_token.return_value = {"video_id": 1, "title": "Shared Video"}
        headers = {
            'Authorization': 'Bearer ' + os.getenv('API_TOKEN', 'supersecretkey')
        }
        response = client.get('/video/share/abcd1234', headers=headers)

        assert response.status_code == 200
        assert response.json == {"video_id": 1, "title": "Shared Video"}


def test_get_video_from_shared_token_not_found(client):
    with patch.object(VideoService, 'get_shared_video_from_token') as mock_get_shared_video_from_token:
        mock_get_shared_video_from_token.side_effect = VideoNotFoundException("Video not found")
        headers = {
            'Authorization': 'Bearer ' + os.getenv('API_TOKEN', 'supersecretkey')
        }
        response = client.get('/video/share/abcd1234', headers=headers)

        assert response.status_code == 404
        assert response.json == {"error": "Video not found"}
