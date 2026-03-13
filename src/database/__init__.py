"""
TokenMeter Database Initialization
"""
from ..database.models import db_manager

def init_db():
    """初始化数据库"""
    db_manager.init_database()
    print("✅ 数据库初始化完成！")

if __name__ == "__main__":
    init_db()