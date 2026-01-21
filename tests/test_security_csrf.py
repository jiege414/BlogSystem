"""
CSRF 安全测试模块

对应回归点：
- BUG-SEC-001：CSRF保护 - 创建文章
- BUG-SEC-002：CSRF保护 - 删除文章
"""

import re
from models import User, Post
from extensions import db


def _extract_csrf_token(html: str) -> str:
    """从 HTML 中提取 CSRF token"""
    m = re.search(r'name="csrf_token".*?value="([^"]+)"', html, re.S)
    assert m, "CSRF token not found in form"
    return m.group(1)


def _register_and_login(client, username="csrfuser", email="csrf@test.com", password="123456"):
    """注册并登录用户"""
    # 注册
    r = client.get("/auth/register")
    token = _extract_csrf_token(r.get_data(as_text=True))
    client.post(
        "/auth/register",
        data={
            "csrf_token": token,
            "username": username,
            "email": email,
            "password": password,
            "password2": password,
        },
        follow_redirects=False,
    )
    # 登录
    r = client.get("/auth/login")
    token = _extract_csrf_token(r.get_data(as_text=True))
    client.post(
        "/auth/login",
        data={"csrf_token": token, "username": username, "password": password},
        follow_redirects=False,
    )


# ==================== 原有测试（保留） ====================

def test_create_post_missing_csrf_returns_400(client):
    """TC-SEC-001: 创建文章缺少 CSRF token 应返回 400"""
    resp = client.post(
        "/blog/create",
        data={"title": "t1", "body": "b1"},
        follow_redirects=False,
    )
    assert resp.status_code == 400


# ==================== 新增测试 ====================

def test_delete_post_missing_csrf_rejected(client, app):
    """TC-SEC-002: 删除文章缺少 CSRF token 应被拒绝（回归 BUG-SEC-002）"""
    # 创建用户和文章
    with app.app_context():
        user = User(username="deletetest", email="delete@test.com")
        user.set_password("123456")
        db.session.add(user)
        db.session.commit()
        
        post = Post(title="To Delete", body="Content", user_id=user.id)
        db.session.add(post)
        db.session.commit()
        post_id = post.id
    
    # 登录
    r = client.get("/auth/login")
    token = _extract_csrf_token(r.get_data(as_text=True))
    client.post(
        "/auth/login",
        data={"csrf_token": token, "username": "deletetest", "password": "123456"},
        follow_redirects=False,
    )
    
    # 尝试删除（不带 CSRF token）
    resp = client.post(f"/blog/post/{post_id}/delete", follow_redirects=False)
    
    # 应该被拒绝（400 或 302 但文章仍存在）
    # 验证文章未被删除
    with app.app_context():
        post = Post.query.get(post_id)
        assert post is not None, "文章不应该被删除（CSRF 未通过）"


def test_create_post_with_valid_csrf_succeeds(client, app):
    """TC-SEC-001 回归: 携带有效 CSRF token 创建文章应成功"""
    _register_and_login(client)
    
    # 获取创建页面和 CSRF token
    r = client.get("/blog/create")
    assert r.status_code == 200
    token = _extract_csrf_token(r.get_data(as_text=True))
    
    # 携带 token 创建文章
    resp = client.post(
        "/blog/create",
        data={"csrf_token": token, "title": "Valid Post", "body": "Valid Content"},
        follow_redirects=False,
    )
    
    # 应该成功并重定向
    assert resp.status_code == 302
    
    # 验证文章已创建
    with app.app_context():
        post = Post.query.filter_by(title="Valid Post").first()
        assert post is not None, "文章应该被成功创建"