"""表单定义文件

本文件包含所有WTForms表单类，用于用户输入验证。
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User


class RegistrationForm(FlaskForm):
    """用户注册表单"""
    
    username = StringField(
        '用户名',
        validators=[
            DataRequired(message='请输入用户名'),
            Length(min=4, max=64, message='用户名长度必须在4-64个字符之间')
        ],
        render_kw={'placeholder': '请输入用户名（4-64个字符）', 'class': 'form-control'}
    )
    
    email = StringField(
        '邮箱',
        validators=[
            DataRequired(message='请输入邮箱地址'),
            Email(message='请输入有效的邮箱地址')
        ],
        render_kw={'placeholder': '请输入邮箱地址', 'class': 'form-control'}
    )
    
    password = PasswordField(
        '密码',
        validators=[
            DataRequired(message='请输入密码'),
            Length(min=6, message='密码长度至少为6个字符')
        ],
        render_kw={'placeholder': '请输入密码（至少6个字符）', 'class': 'form-control'}
    )
    
    password2 = PasswordField(
        '确认密码',
        validators=[
            DataRequired(message='请再次输入密码'),
            EqualTo('password', message='两次输入的密码不一致')
        ],
        render_kw={'placeholder': '请再次输入密码', 'class': 'form-control'}
    )
    
    submit = SubmitField('注册', render_kw={'class': 'btn btn-primary'})
    
    def validate_username(self, username):
        """验证用户名是否已存在"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请选择其他用户名。')
    
    def validate_email(self, email):
        """验证邮箱是否已被注册"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已被注册，请使用其他邮箱或直接登录。')


class LoginForm(FlaskForm):
    """用户登录表单"""
    
    username = StringField(
        '用户名',
        validators=[DataRequired(message='请输入用户名')],
        render_kw={'placeholder': '请输入用户名', 'class': 'form-control'}
    )
    
    password = PasswordField(
        '密码',
        validators=[DataRequired(message='请输入密码')],
        render_kw={'placeholder': '请输入密码', 'class': 'form-control'}
    )
    
    submit = SubmitField('登录', render_kw={'class': 'btn btn-primary'})


class PostForm(FlaskForm):
    """文章创建表单"""
    
    title = StringField(
        '标题',
        validators=[
            DataRequired(message='请输入文章标题'),
            Length(min=1, max=200, message='标题长度必须在1-200个字符之间')
        ],
        render_kw={'placeholder': '请输入文章标题（最多200个字符）', 'class': 'form-control'}
    )
    
    body = TextAreaField(
        '内容',
        validators=[
            DataRequired(message='请输入文章内容'),
            Length(min=1, message='文章内容不能为空')
        ],
        render_kw={'placeholder': '请输入文章内容', 'class': 'form-control', 'rows': 10}
    )
    
    submit = SubmitField('发布文章', render_kw={'class': 'btn btn-primary'})

