"""
pytest 测试配置文件

重要：测试使用完全独立的临时数据库，不会影响主数据库 (instance/blog.db)
"""

import os
import tempfile

import pytest

from extensions import db


@pytest.fixture
def app():
    """创建测试用的 Flask 应用实例，使用独立的临时数据库"""
    # 先创建临时数据库文件
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    
    # 设置环境变量，让 create_app 使用临时数据库
    # 注意：必须在 import create_app 之前或通过配置覆盖
    os.environ['DATABASE_URL'] = f"sqlite:///{db_path}"
    
    # 延迟导入，确保配置生效
    from app import create_app
    
    # 创建应用，并立即覆盖数据库配置
    app = create_app()
    
    # 强制覆盖数据库 URI（确保使用临时数据库）
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 重新绑定引擎到新的数据库 URI
    with app.app_context():
        # 使用 db.engine.dispose() 确保旧连接被关闭
        db.engine.dispose()
        # 现在 drop_all 和 create_all 会作用于临时数据库
        db.drop_all()
        db.create_all()

    yield app

    # 清理：关闭并删除临时数据库
    with app.app_context():
        db.engine.dispose()
    os.close(db_fd)
    os.unlink(db_path)
    
    # 清理环境变量
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()