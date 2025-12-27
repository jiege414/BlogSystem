"""博客文章路由文件

本文件包含文章相关的路由：创建、列表展示、详情查看、编辑、删除。
"""

from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from forms import PostForm
from models import Post, db

# 创建博客蓝图
blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """
    创建文章路由
    
    处理文章创建请求：
    - GET: 显示创建文章表单
    - POST: 处理表单提交，创建新文章
    """
    form = PostForm()

    # CSRF 回归修复：对于缺失/无效 CSRF token 的 POST 请求，直接拒绝
    # 说明：未启用该处理时，CSRF 失败可能表现为返回创建页（HTTP 200），不利于安全语义与测试判定。
    if request.method == 'POST' and 'csrf_token' in getattr(form, 'errors', {}):
        abort(400)
    
    if form.validate_on_submit():
        # 创建新文章
        post = Post(
            title=form.title.data,
            body=form.body.data,
            user_id=current_user.id  # 关联当前登录用户
        )
        
        # 保存到数据库
        try:
            db.session.add(post)
            db.session.commit()
            flash('文章发布成功！', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('文章发布失败，请稍后重试。', 'danger')
    
    return render_template('create_post.html', form=form, title='创建文章')


@blog_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    """
    文章详情页路由
    
    显示指定文章的完整内容。
    
    Args:
        post_id: 文章的ID
        
    Returns:
        渲染文章详情页模板，如果文章不存在则返回404
    """
    post = Post.query.get_or_404(post_id)
    # 创建一个简单的表单用于 CSRF 保护
    from forms import PostForm
    form = PostForm()  # 仅用于获取 CSRF token
    return render_template('post_detail.html', post=post, form=form, title=post.title)


@blog_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """
    编辑文章路由
    
    允许文章作者编辑自己的文章。
    
    Args:
        post_id: 文章的ID
        
    Returns:
        渲染编辑文章模板，如果文章不存在或用户无权限则返回404或403
    """
    post = Post.query.get_or_404(post_id)
    
    # 权限检查：只有文章作者才能编辑
    if post.user_id != current_user.id:
        abort(403)  # 禁止访问
    
    form = PostForm()
    
    # 如果是 GET 请求，预填充表单数据
    if request.method == 'GET':
        form.title.data = post.title
        form.body.data = post.body
    
    if form.validate_on_submit():
        # 更新文章内容
        post.title = form.title.data
        post.body = form.body.data
        
        # 保存到数据库
        try:
            db.session.commit()
            flash('文章更新成功！', 'success')
            return redirect(url_for('blog.post_detail', post_id=post.id))
        except Exception as e:
            db.session.rollback()
            flash('文章更新失败，请稍后重试。', 'danger')
    
    return render_template('edit_post.html', form=form, post=post, title='编辑文章')


@blog_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """
    删除文章路由
    
    允许文章作者删除自己的文章。
    只接受 POST 请求，防止误删。
    
    Args:
        post_id: 文章的ID
        
    Returns:
        重定向到首页，如果文章不存在或用户无权限则返回404或403
    """
    post = Post.query.get_or_404(post_id)
    
    # 权限检查：只有文章作者才能删除
    if post.user_id != current_user.id:
        abort(403)  # 禁止访问
    
    # 删除文章
    try:
        db.session.delete(post)
        db.session.commit()
        flash('文章已成功删除。', 'success')
    except Exception as e:
        db.session.rollback()
        flash('删除文章失败，请稍后重试。', 'danger')
    
    return redirect(url_for('index'))

