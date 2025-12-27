"""认证相关路由：注册、登录、登出。"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from forms import RegistrationForm, LoginForm
from models import User, db

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册。"""
    # 如果用户已登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # 创建新用户
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        # 使用模型中的方法设置密码（会自动哈希）
        user.set_password(form.password.data)
        
        # 保存到数据库
        try:
            db.session.add(user)
            db.session.commit()
            flash('注册成功！请登录。', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('注册失败，请稍后重试。', 'danger')
    
    return render_template('register.html', form=form, title='用户注册')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录（支持 next 重定向）。"""
    # 如果用户已登录，重定向到首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # 查找用户（支持用户名或邮箱登录）
        user = User.query.filter_by(username=form.username.data).first()
        
        # 如果用户名不存在，尝试用邮箱查找
        if user is None:
            user = User.query.filter_by(email=form.username.data).first()
        
        # 验证用户存在且密码正确
        if user and user.check_password(form.password.data):
            # 使用 Flask-Login 登录用户
            login_user(user, remember=True)  # remember=True 表示记住登录状态
            
            # next 参数仅允许站内相对路径，避免开放重定向
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')
            
            flash(f'欢迎回来，{user.username}！', 'success')
            return redirect(next_page)
        else:
            flash('用户名或密码错误，请重试。', 'danger')
    
    return render_template('login.html', form=form, title='用户登录')


@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出。"""
    logout_user()
    flash('您已成功登出。', 'info')
    return redirect(url_for('index'))

