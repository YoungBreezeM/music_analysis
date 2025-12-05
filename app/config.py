import os
import logging
from datetime import datetime

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///music_analysis.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # JSON编码配置，解决中文乱码问题
    JSON_AS_ASCII = False
    JSONIFY_MIMETYPE = 'application/json;charset=utf-8'
    
    # 日志配置
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    LOG_FILE = os.path.join(LOG_DIR, f'app_{datetime.now().strftime("%Y%m%d")}.log')
    
    @staticmethod
    def init_app(app):
        # 确保日志目录存在
        if not os.path.exists(Config.LOG_DIR):
            os.makedirs(Config.LOG_DIR)
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(Config.LOG_FILE),
                logging.StreamHandler()
            ]
        )

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}