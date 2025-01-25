from flask import Blueprint, request, jsonify
from app.services.video_service import upload_video, trim_video, merge_videos

video_routes = Blueprint('video_routes', __name__)

@video_routes.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file:
        response = upload_video(file)
        return jsonify(response), 201
    return jsonify({"message": "Invalid file"}), 400

@video_routes.route('/trim/<int:video_id>', methods=['POST'])
def trim(video_id):
    start = request.json.get('start')
    end = request.json.get('end')
    if start and end:
        response = trim_video(video_id, start, end)
        return jsonify(response), 200
    return jsonify({"message": "Invalid parameters"}), 400

@video_routes.route('/merge', methods=['POST'])
def merge():
    video_ids = request.json.get('video_ids')
    if video_ids:
        response = merge_videos(video_ids)
        return jsonify(response), 200
    return jsonify({"message": "Invalid parameters"}), 400
