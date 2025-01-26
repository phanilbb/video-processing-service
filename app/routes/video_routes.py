from flask import Blueprint, request, jsonify

from app.exceptions.video_exceptions import VideoValidationException, VideoProcessingException, VideoNotFoundException
from app.service.video_service import VideoService
from app.authentication import authenticate

video_routes = Blueprint('video_routes', __name__)


@video_routes.route('/video', methods=['POST'])
@authenticate
def upload():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({"message": "Invalid file"}), 400
        video_service = VideoService()
        response = video_service.upload_video(file)
        return jsonify(response), 201
    except VideoValidationException as e:
        return jsonify({"error": e.message}), 400
    except VideoProcessingException as e:
        return jsonify({"error": e.message}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@video_routes.route('/video/<int:video_id>', methods=['GET'])
@authenticate
def get(video_id):
    try:
        video_service = VideoService()
        response = video_service.get_video(video_id)
        return jsonify(response), 200
    except VideoNotFoundException as e:
        return jsonify({"error": e.message}), 404
    except VideoProcessingException as e:
        return jsonify({"error": e.message}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@video_routes.route('/trim/<int:video_id>', methods=['POST'])
def trim(video_id):
    start = request.json.get('start')
    end = request.json.get('end')
    if start and end:
        video_service = VideoService()
        response = video_service.trim_video(video_id, start, end)
        return jsonify(response), 200
    return jsonify({"message": "Invalid parameters"}), 400


@video_routes.route('/merge', methods=['POST'])
def merge():
    video_ids = request.json.get('video_ids')
    if video_ids:
        video_service = VideoService()
        response = video_service.merge_videos(video_ids)
        return jsonify(response), 200
    return jsonify({"message": "Invalid parameters"}), 400
