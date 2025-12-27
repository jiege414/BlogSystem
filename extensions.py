"""Flask扩展实例定义文件

本文件集中管理所有Flask扩展的实例，避免循环导入问题。
这是Flask应用工厂模式的最佳实践。
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

# 创建数据库实例（在应用工厂中初始化）
db = SQLAlchemy()

# 创建登录管理器实例（在应用工厂中初始化）
login_manager = LoginManager()
csrf = CSRFProtect()    
