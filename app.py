"""Flask 博客应用入口。

使用应用工厂模式创建 app，并初始化扩展（SQLAlchemy / Login / CSRF）。
"""

import os

from flask import Flask, render_template

from extensions import csrf, db, login_manager


def create_app():
    """创建并配置 Flask 应用实例（应用工厂）。"""
    app = Flask(__name__)

    # 确保 instance 文件夹存在
    os.makedirs(app.instance_path, exist_ok=True)

    # 基础配置 - 使用绝对路径，避免工作目录问题
    db_path = os.path.join(app.instance_path, "blog.db")
    app.config.from_mapping(
        SECRET_KEY="dev-secret-key-change-in-production",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "请先登录以访问此页面。"
    
    @login_manager.user_loader
    def load_user(user_id):
        """Flask-Login 回调：通过用户 ID 加载用户对象。"""
        from models import User

        return User.query.get(int(user_id))

    # 注册蓝图
    from auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from blog import blog_bp

    app.register_blueprint(blog_bp, url_prefix="/blog")

    from models import Post, User

    @app.route("/")
    def index():
        posts = Post.query.order_by(Post.timestamp.desc()).all()
        return render_template("index.html", posts=posts)

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        print("Initialized the database.")

    return app
