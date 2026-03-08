"""Flask 博客应用入口。

使用应用工厂模式创建 app，并初始化扩展（SQLAlchemy / Login / CSRF）。
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, request, send_from_directory

from app.extensions import csrf, db, login_manager


def create_app():
    """创建并配置 Flask 应用实例（应用工厂）。"""
    # 获取当前文件所在目录的父目录（项目根目录）
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(__name__, 
                template_folder=os.path.join(base_dir, 'templates'),
                static_folder=os.path.join(base_dir, 'static'))

    # 确保 instance 文件夹存在
    os.makedirs(app.instance_path, exist_ok=True)

    # 数据库配置：生产环境用 PostgreSQL，本地用 SQLite
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Render 提供的 PostgreSQL（需要替换协议）
        db_url = database_url.replace('postgres://', 'postgresql://')
    else:
        # 本地开发用 SQLite
        db_path = os.path.join(app.instance_path, "blog.db")
        db_url = f"sqlite:///{db_path}"

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        SQLALCHEMY_DATABASE_URI=db_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # 配置日志
    if not app.debug:
        # 生产环境：写入日志文件
        log_dir = os.path.join(app.instance_path, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'blog.log'),
            maxBytes=10240,  # 10KB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('博客系统启动')
    else:
        # 开发环境：输出到控制台
        logging.basicConfig(level=logging.DEBUG)
        app.logger.setLevel(logging.DEBUG)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "请先登录以访问此页面。"
    
    @login_manager.user_loader
    def load_user(user_id):
        """Flask-Login 回调：通过用户 ID 加载用户对象。"""
        from app.models import User

        return User.query.get(int(user_id))

    # 注册蓝图
    from app.auth import auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.blog import blog_bp

    app.register_blueprint(blog_bp, url_prefix="/blog")

    from app.models import Post, User

    @app.route("/")
    def index():
        search_query = request.args.get('q', '').strip()
        if search_query:
            # 模糊查询标题
            posts = Post.query.filter(
                Post.title.contains(search_query)
            ).order_by(Post.timestamp.desc()).all()
        else:
            posts = Post.query.order_by(Post.timestamp.desc()).all()
        return render_template("index.html", posts=posts, search_query=search_query)

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(base_dir, 'static'), 'favicon.ico',
                                   mimetype='image/vnd.microsoft.icon')

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()

    return app
