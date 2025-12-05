from flask import Flask, jsonify
from flask_cors import CORS
from .config import config
from .models import db
from .routes import register_blueprints
from .utils.logger import get_logger

logger = get_logger(__name__)

def create_app(config_name='default'):
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    

    
    # 初始化配置
    config[config_name].init_app(app)
    
    # 初始化数据库
    db.init_app(app)
    
    # 启用CORS
    CORS(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        logger.info("Database tables created")
    
    # 健康检查路由
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy'}), 200
    
    logger.info("Flask app initialized")
    return app