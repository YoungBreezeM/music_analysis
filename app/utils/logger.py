import logging

# 创建自定义日志记录器
def get_logger(name):
    logger = logging.getLogger(name)
    return logger