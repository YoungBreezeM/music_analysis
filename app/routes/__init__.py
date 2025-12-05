from flask import Blueprint
from .music import music_bp
from .analysis import analysis_bp

# 注册所有蓝图
def register_blueprints(app):
    app.register_blueprint(music_bp, url_prefix='/api/music')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')