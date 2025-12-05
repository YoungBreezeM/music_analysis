from flask import Blueprint, jsonify, request
from ..models import db, Music
from ..utils.logger import get_logger

music_bp = Blueprint('music', __name__)
logger = get_logger(__name__)

@music_bp.route('/', methods=['GET'])
def get_all_music():
    try:
        music_list = Music.query.all()
        return jsonify([music.to_dict() for music in music_list]), 200
    except Exception as e:
        logger.error(f"Error fetching music list: {str(e)}")
        return jsonify({'error': 'Failed to fetch music list'}), 500

@music_bp.route('/<int:id>', methods=['GET'])
def get_music(id):
    try:
        music = Music.query.get_or_404(id)
        return jsonify(music.to_dict()), 200
    except Exception as e:
        logger.error(f"Error fetching music {id}: {str(e)}")
        return jsonify({'error': 'Music not found'}), 404

@music_bp.route('/', methods=['POST'])
def create_music():
    try:
        data = request.get_json()
        new_music = Music(
            title=data.get('title'),
            artist=data.get('artist'),
            album=data.get('album'),
            duration=data.get('duration')
        )
        db.session.add(new_music)
        db.session.commit()
        logger.info(f"Created new music: {new_music.title} by {new_music.artist}")
        return jsonify(new_music.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating music: {str(e)}")
        return jsonify({'error': 'Failed to create music'}), 400

@music_bp.route('/<int:id>', methods=['PUT'])
def update_music(id):
    try:
        music = Music.query.get_or_404(id)
        data = request.get_json()
        
        music.title = data.get('title', music.title)
        music.artist = data.get('artist', music.artist)
        music.album = data.get('album', music.album)
        music.duration = data.get('duration', music.duration)
        
        db.session.commit()
        logger.info(f"Updated music: {music.title} (ID: {id})")
        return jsonify(music.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating music {id}: {str(e)}")
        return jsonify({'error': 'Failed to update music'}), 400

@music_bp.route('/<int:id>', methods=['DELETE'])
def delete_music(id):
    try:
        music = Music.query.get_or_404(id)
        db.session.delete(music)
        db.session.commit()
        logger.info(f"Deleted music: {music.title} (ID: {id})")
        return jsonify({'message': 'Music deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting music {id}: {str(e)}")
        return jsonify({'error': 'Failed to delete music'}), 400