"""Flask 博客应用入口。

使用应用工厂模式创建 app，并初始化扩展（SQLAlchemy / Login / CSRF）。
"""

import os

from flask import Flask, render_template, request

from extensions import csrf, db, login_manager


def create_app():
    """创建并配置 Flask 应用实例（应用工厂）。"""
    app = Flask(__name__)

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
        search_query = request.args.get('q', '').strip()
        if search_query:
            # 模糊查询标题
            posts = Post.query.filter(
                Post.title.contains(search_query)
            ).order_by(Post.timestamp.desc()).all()
        else:
            posts = Post.query.order_by(Post.timestamp.desc()).all()
        return render_template("index.html", posts=posts, search_query=search_query)

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        print("Initialized the database.")

    return app
