# Music Analysis API

一个使用Flask构建的音乐分析API后端项目，包含ORM、SQLite数据库和日志功能。

## 功能特性

- **RESTful API**: 提供音乐和分析数据的增删改查操作
- **数据库**: 使用SQLite作为数据库，SQLAlchemy作为ORM
- **日志系统**: 记录应用运行日志，支持文件和控制台输出
- **跨域支持**: 配置了CORS，支持前端跨域请求

## 项目结构

```
music_analysis/
├── app/                    # 应用主目录
│   ├── __init__.py         # 应用初始化
│   ├── config.py           # 配置文件
│   ├── models/             # 数据库模型
│   │   ├── __init__.py
│   │   ├── database.py     # 数据库实例
│   │   ├── music.py        # 音乐模型
│   │   └── analysis.py     # 分析模型
│   ├── routes/             # API路由
│   │   ├── __init__.py
│   │   ├── music.py        # 音乐相关路由
│   │   └── analysis.py     # 分析相关路由
│   └── utils/              # 工具函数
│       └── logger.py       # 日志工具
├── logs/                   # 日志目录
├── .env.example            # 环境变量示例
├── requirements.txt        # 依赖包列表
├── run.py                  # 应用入口
└── README.md               # 项目说明
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制并编辑环境变量文件：

```bash
cp .env.example .env
# 编辑.env文件，设置相应的环境变量
```

### 3. 启动应用

```bash
python run.py
```

应用将在 http://localhost:5000 启动。

## API 接口

### 音乐相关接口

- **GET /api/music/**: 获取所有音乐
- **GET /api/music/<id>**: 获取指定ID的音乐
- **POST /api/music/**: 创建新音乐
- **PUT /api/music/<id>**: 更新指定ID的音乐
- **DELETE /api/music/<id>**: 删除指定ID的音乐

### 分析相关接口

- **GET /api/analysis/**: 获取所有分析记录
- **GET /api/analysis/<id>**: 获取指定ID的分析记录
- **GET /api/analysis/music/<music_id>**: 获取指定音乐的所有分析记录
- **POST /api/analysis/**: 创建新的分析记录
- **DELETE /api/analysis/<id>**: 删除指定ID的分析记录

### 健康检查

- **GET /health**: 健康检查接口

## 数据库模型

### Music

- **id**: 主键
- **title**: 音乐标题
- **artist**: 艺术家
- **album**: 专辑
- **duration**: 时长（秒）
- **created_at**: 创建时间
- **updated_at**: 更新时间

### Analysis

- **id**: 主键
- **music_id**: 关联音乐ID
- **tempo**: 节奏速度
- **key**: 调性
- **energy**: 能量值
- **danceability**: 舞蹈性
- **valence**: 情感倾向
- **created_at**: 创建时间