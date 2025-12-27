"""Flask博客应用主文件

这是Flask应用的主入口文件，包含应用实例的创建和基本配置。
"""

from flask import Flask, render_template
from extensions import db, login_manager, csrf


def create_app():
    """
    应用工厂函数：创建并配置Flask应用实例
    
    这是Flask推荐的应用创建方式，便于测试和配置管理。
    
    Returns:
        Flask: 配置好的Flask应用实例
    """
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # ========== 配置部分 ==========
    # 设置密钥（用于会话加密，生产环境应该使用环境变量）
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    
    # 配置数据库URI（SQLite数据库，存储在instance文件夹中）
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
    # 禁用SQLAlchemy事件系统（可选，提升性能）
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # ========== 初始化扩展 ==========
    # 初始化数据库
    db.init_app(app)
    
    # 初始化登录管理器
    login_manager.init_app(app)
    # 初始化 CSRF 保护（全局）
    csrf.init_app(app)
    # 设置登录视图（当用户需要登录时，重定向到这个路由）
    login_manager.login_view = 'auth.login'
    # 设置登录提示消息的类别
    login_manager.login_message = '请先登录以访问此页面。'
    
    # 定义用户加载回调函数（Flask-Login 必需）
    @login_manager.user_loader
    def load_user(user_id):
        """
        根据用户ID加载用户对象
        
        这是Flask-Login必需的回调函数，用于从会话中恢复用户对象。
        
        Args:
            user_id: 用户的ID（字符串形式）
            
        Returns:
            User: 用户对象，如果不存在则返回None
        """
        from models import User
        return User.query.get(int(user_id))
    
    # ========== 注册蓝图 ==========
    # 注册认证蓝图
    from auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # 注册博客蓝图
    from blog import blog_bp
    app.register_blueprint(blog_bp, url_prefix='/blog')
    
    # 避免循环导入，在应用和 db 初始化之后再导入模型
    from models import Post

    # ========== 注册路由（基础首页路由）==========
    @app.route("/")
    def index():
        """首页路由：展示最新文章列表"""
        posts = Post.query.order_by(Post.timestamp.desc()).all()
        return render_template("index.html", posts=posts)
    
    return app


# 创建应用实例（用于直接运行此文件时）
if __name__ == '__main__':
    app = create_app()
    # 在应用上下文中创建数据库表（如果尚未创建）
    with app.app_context():
        # 导入所有模型类，确保 SQLAlchemy 知道要创建哪些表
        from models import User, Post
        # 使用已初始化的 db 实例创建所有表
        db.create_all()
    # 开发模式运行（开启调试模式）
    app.run(debug=True)