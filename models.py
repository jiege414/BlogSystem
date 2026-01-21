"""
数据模型定义文件

本文件包含博客系统的核心数据模型：
- User：用户模型
- Post：文章模型
"""

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class User(UserMixin, db.Model):
    """用户模型"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    posts = db.relationship("Post", backref="author", lazy="dynamic")

    def set_password(self, password: str) -> None:
        """
        设置用户密码（使用哈希加密）
        
        Args:
            password: 原始密码字符串
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """
        验证用户密码是否正确
        
        Args:
            password: 待验证的密码字符串
            
        Returns:
            bool: 密码正确返回True，否则返回False
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class Post(db.Model):
    """文章模型"""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self) -> str:
        return f"<Post {self.title[:20]}>"


