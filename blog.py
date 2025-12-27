"""文章相关路由：创建、详情、编辑、删除。"""

from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from forms import PostForm
from models import Post, db

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """创建文章。"""
    form = PostForm()

    # POST 且 CSRF 无效时直接返回 400
    if request.method == 'POST' and 'csrf_token' in getattr(form, 'errors', {}):
        abort(400)

    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data, user_id=current_user.id)
        try:
            db.session.add(post)
            db.session.commit()
            flash('文章发布成功！', 'success')
            return redirect(url_for('index'))
        except Exception:
            db.session.rollback()
            flash('文章发布失败，请稍后重试。', 'danger')

    return render_template('create_post.html', form=form, title='创建文章')


@blog_bp.route('/post/<int:post_id>')
def post_detail(post_id):
    """文章详情。"""
    post = Post.query.get_or_404(post_id)
    form = PostForm()  # 仅用于 CSRF token
    return render_template('post_detail.html', post=post, form=form, title=post.title)


@blog_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """编辑文章（仅作者）。"""
    post = Post.query.get_or_404(post_id)

    # 如果当前用户不是作者，禁止编辑
    if post.user_id != current_user.id:
        abort(403)

    form = PostForm()

    # 如果是 GET 请求，预填充表单
    if request.method == 'GET':
        form.title.data = post.title
        form.body.data = post.body

    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        try:
            db.session.commit()
            flash('文章更新成功！', 'success')
            return redirect(url_for('blog.post_detail', post_id=post.id))
        except Exception:
            db.session.rollback()
            flash('文章更新失败，请稍后重试。', 'danger')

    return render_template('edit_post.html', form=form, post=post, title='编辑文章')


@blog_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """删除文章（仅作者，POST）。"""
    post = Post.query.get_or_404(post_id)

    # 如果当前用户不是作者，禁止删除
    if post.user_id != current_user.id:
        abort(403)

    try:
        db.session.delete(post)
        db.session.commit()
        flash('文章已成功删除。', 'success')
    except Exception:
        db.session.rollback()
        flash('删除文章失败，请稍后重试。', 'danger')

    return redirect(url_for('index'))

