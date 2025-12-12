from math import log
from flask import Blueprint, jsonify, request, Response
import asyncio
import json
from ..models import db, Analysis, Music
from ..pkg.analysis import analyze_music_url
from ..utils.logger import get_logger

analysis_bp = Blueprint('analysis', __name__)
logger = get_logger(__name__)

@analysis_bp.route('/', methods=['GET'])
def get_all_analyses():
    try:
        analyses = Analysis.query.all()
        return jsonify([analysis.to_dict() for analysis in analyses]), 200
    except Exception as e:
        logger.error(f"Error fetching analyses: {str(e)}")
        return jsonify({'error': 'Failed to fetch analyses'}), 500

@analysis_bp.route('/<int:id>', methods=['GET'])
def get_analysis(id):
    try:
        analysis = Analysis.query.get_or_404(id)
        return jsonify(analysis.to_dict()), 200
    except Exception as e:
        logger.error(f"Error fetching analysis {id}: {str(e)}")
        return jsonify({'error': 'Analysis not found'}), 404

@analysis_bp.route('/music/<int:music_id>', methods=['GET'])
def get_analyses_by_music(music_id):
    try:
        # 先检查音乐是否存在
        music = Music.query.get_or_404(music_id)
        analyses = Analysis.query.filter_by(music_id=music_id).all()
        return jsonify([analysis.to_dict() for analysis in analyses]), 200
    except Exception as e:
        logger.error(f"Error fetching analyses for music {music_id}: {str(e)}")
        return jsonify({'error': 'Failed to fetch analyses'}), 404

@analysis_bp.route('/', methods=['POST'])
def create_analysis():
    try:
        data = request.get_json()
        
        # 检查音乐是否存在
        music = Music.query.get_or_404(data.get('music_id'))
        
        new_analysis = Analysis(
            music_id=data.get('music_id'),
            tempo=data.get('tempo'),
            key=data.get('key'),
            energy=data.get('energy'),
            danceability=data.get('danceability'),
            valence=data.get('valence')
        )
        
        db.session.add(new_analysis)
        db.session.commit()
        logger.info(f"Created analysis for music ID: {data.get('music_id')}")
        return jsonify(new_analysis.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating analysis: {str(e)}")
        return jsonify({'error': 'Failed to create analysis'}), 400

@analysis_bp.route('/<int:id>', methods=['DELETE'])
def delete_analysis(id):
    try:
        analysis = Analysis.query.get_or_404(id)
        db.session.delete(analysis)
        db.session.commit()
        logger.info(f"Deleted analysis ID: {id}")
        return jsonify({'message': 'Analysis deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting analysis {id}: {str(e)}")
        return jsonify({'error': 'Failed to delete analysis'}), 400

@analysis_bp.route('/<int:id>', methods=['PUT'])
def update_analysis(id):
    try:
        analysis = Analysis.query.get_or_404(id)
        data = request.get_json()
        
        analysis.tempo = data.get('tempo', analysis.tempo)
        analysis.key = data.get('key', analysis.key)
        analysis.energy = data.get('energy', analysis.energy)
        analysis.danceability = data.get('danceability', analysis.danceability)
        analysis.valence = data.get('valence', analysis.valence)
        
        db.session.commit()
        logger.info(f"Updated analysis ID: {id}")
        return jsonify(analysis.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating analysis {id}: {str(e)}")
        return jsonify({'error': 'Failed to update analysis'}), 400

@analysis_bp.route('/analyze-url', methods=['POST'])
def analyze_url():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        logger.info(f"Analyzing URL: {url}")
        
        # 运行异步分析函数
        analysis_result = asyncio.run(analyze_music_url(url))
        logger.warning(f"Analysis result: {analysis_result}")
        if not analysis_result:
            return jsonify({'error': 'Failed to analyze URL'}), 500
        
        # 手动处理JSON编码，确保中文正确显示
        response_data = json.dumps(analysis_result, ensure_ascii=False)
        return Response(response_data, content_type='application/json;charset=utf-8'), 200
    except Exception as e:
        logger.error(f"Error analyzing URL: {str(e)}")
        return jsonify({'error': 'Failed to analyze URL'}), 500