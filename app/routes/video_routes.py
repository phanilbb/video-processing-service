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


@video_routes.route('/video/<int:video_id>/trim', methods=['POST'])
@authenticate
def trim(video_id):
    try:
        start = request.json.get('start')
        end = request.json.get('end')
        if not start or not end:
            return jsonify({"error": "Invalid parameters : 'start' and 'end' are mandatory required fields"}), 400
        video_service = VideoService()
        response = video_service.trim_video(video_id, start, end)
        return jsonify(response), 200

    except VideoNotFoundException as e:
        return jsonify({"error": e.message}), 404
    except VideoProcessingException as e:
        return jsonify({"error": e.message}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@video_routes.route('/videos/merge', methods=['POST'])
@authenticate
def merge():

    try:
        video_ids = request.json.get('video_ids')
        if not video_ids :
            return jsonify({"error": "Invalid parameters : 'video_ids' is a mandatory required field"}), 400
        video_service = VideoService()
        response = video_service.merge_videos(video_ids)
        return jsonify(response), 200

    except VideoNotFoundException as e:
        return jsonify({"error": e.message}), 404
    except VideoProcessingException as e:
        return jsonify({"error": e.message}), 500
    except VideoValidationException as e:
        return jsonify({"error": e.message}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@video_routes.route('/video/<int:video_id>/share', methods=['POST'])
@authenticate
def get_share_link(video_id):
    try:
        video_service = VideoService()
        response = video_service.generate_shareable_link(video_id)
        return jsonify(response), 200

    except VideoNotFoundException as e:
        return jsonify({"error": e.message}), 404
    except VideoProcessingException as e:
        return jsonify({"error": e.message}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@video_routes.route('/video/share/<token>', methods=['GET'])
@authenticate
def get_video_from_shared_token(token):
    try:
        video_service = VideoService()
        response = video_service.get_shared_video_from_token(token)
        return jsonify(response), 200

    except VideoNotFoundException as e:
        return jsonify({"error": e.message}), 404
    except VideoProcessingException as e:
        return jsonify({"error": e.message}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

