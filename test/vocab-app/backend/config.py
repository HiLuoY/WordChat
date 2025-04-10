# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'yj5211314',  # 修改为您的实际MySQL密码
    'database': 'elp',
    'charset': 'utf8mb4',
    'cursorclass': 'DictCursor'
}

# Flask配置
FLASK_CONFIG = {
    'SECRET_KEY': 'your-secret-key',
    'JSON_AS_ASCII': False
}

# WebSocket配置
SOCKET_CONFIG = {
    'cors_allowed_origins': '*'
} 