"""Flask 博客应用入口。

使用应用工厂模式创建 app，并初始化扩展（SQLAlchemy / Login / CSRF）。
"""

from flask import Flask, render_template
from extensions import db, login_manager, csrf


def create_app():
    """创建并配置 Flask 应用实例（应用工厂）。"""
    app = Flask(__name__)

    # 基础配置
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录以访问此页面。'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Flask-Login 回调：通过用户 ID 加载用户对象。"""
        from models import User
        return User.query.get(int(user_id))

    # 注册蓝图
    from auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from blog import blog_bp
    app.register_blueprint(blog_bp, url_prefix='/blog')

    from models import Post

    @app.route("/")
    def index():
        posts = Post.query.order_by(Post.timestamp.desc()).all()
        return render_template("index.html", posts=posts)

    return app



if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        from models import User, Post
        db.create_all()
    app.run(debug=True)