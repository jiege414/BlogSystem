"""
最小回归集测试模块

覆盖核心功能路径：
- 用户注册、登录、登出
- 文章创建、查看、编辑、删除
- 权限控制
- 登录 next 参数跳转（BUG-UX-001 回归）
"""

import re
from models import User, Post
from extensions import db


def _extract_csrf_token(html: str) -> str:
    """从 HTML 中提取 CSRF token"""
    m = re.search(r'name="csrf_token".*?value="([^"]+)"', html, re.S)
    assert m, "CSRF token not found in form"
    return m.group(1)


# ==================== 用户认证测试 ====================

def test_register_success(client, app):
    """TC-AUTH-001: 用户注册 - 正常流程"""
    r = client.get("/auth/register")
    assert r.status_code == 200
    token = _extract_csrf_token(r.get_data(as_text=True))
    
    resp = client.post(
        "/auth/register",
        data={
            "csrf_token": token,
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "123456",
            "password2": "123456",
        },
        follow_redirects=False,
    )
    
    # 注册成功应重定向到登录页
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers.get("Location", "")
    
    # 验证用户已创建
    with app.app_context():
        user = User.query.filter_by(username="newuser").first()
        assert user is not None
        assert user.email == "newuser@test.com"


def test_login_success(client, app):
    """TC-AUTH-008: 用户登录 - 正常流程"""
    # 先创建用户
    with app.app_context():
        user = User(username="loginuser", email="login@test.com")
        user.set_password("123456")
        db.session.add(user)
        db.session.commit()
    
    # 登录
    r = client.get("/auth/login")
    token = _extract_csrf_token(r.get_data(as_text=True))
    
    resp = client.post(
        "/auth/login",
        data={"csrf_token": token, "username": "loginuser", "password": "123456"},
        follow_redirects=False,
    )
    
    # 登录成功应重定向到首页
    assert resp.status_code == 302
    
    # 验证已登录（可访问受保护页面）
    resp = client.get("/blog/create")
    assert resp.status_code == 200


def test_logout_success(client, app):
    """TC-AUTH-012: 用户登出"""
    # 创建并登录用户
    with app.app_context():
        user = User(username="logoutuser", email="logout@test.com")
        user.set_password("123456")
        db.session.add(user)
        db.session.commit()
    
    r = client.get("/auth/login")
    token = _extract_csrf_token(r.get_data(as_text=True))
    client.post(
        "/auth/login",
        data={"csrf_token": token, "username": "logoutuser", "password": "123456"},
        follow_redirects=False,
    )
    
    # 登出
    resp = client.get("/auth/logout", follow_redirects=False)
    assert resp.status_code == 302
    
    # 验证已登出（无法访问受保护页面）
    resp = client.get("/blog/create", follow_redirects=False)
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers.get("Location", "")


def test_protected_page_requires_login(client):
    """TC-AUTH-013: 未登录用户访问受保护页面"""
    resp = client.get("/blog/create", follow_redirects=False)
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers.get("Location", "")


def test_login_with_next_parameter(client, app):
    """TC-UX-006 / BUG-UX-001 回归: 登录后按 next 参数跳转"""
    # 创建用户
    with app.app_context():
        user = User(username="nextuser", email="next@test.com")
        user.set_password("123456")
        db.session.add(user)
        db.session.commit()
    
    # 先访问受保护页面，应重定向到登录页并带 next 参数
    resp = client.get("/blog/create", follow_redirects=False)
    assert resp.status_code == 302
    login_url = resp.headers.get("Location", "")
    assert "next=" in login_url or "next%3D" in login_url.lower()
    
    # 访问带 next 参数的登录页
    r = client.get("/auth/login?next=/blog/create")
    token = _extract_csrf_token(r.get_data(as_text=True))
    
    # 登录
    resp = client.post(
        "/auth/login?next=/blog/create",
        data={"csrf_token": token, "username": "nextuser", "password": "123456"},
        follow_redirects=False,
    )
    
    # 应跳转到 next 指定的页面
    assert resp.status_code == 302
    location = resp.headers.get("Location", "")
    assert "/blog/create" in location, f"应跳转到 /blog/create，实际: {location}"


# ==================== 文章管理测试 ====================

def test_view_post_list(client, app):
    """TC-POST-005: 查看文章列表"""
    # 创建一些文章
    with app.app_context():
        user = User(username="listuser", email="list@test.com")
        user.set_password("123456")
        db.session.add(user)
        db.session.commit()
        
        post1 = Post(title="First Post", body="Content 1", user_id=user.id)
        post2 = Post(title="Second Post", body="Content 2", user_id=user.id)
        db.session.add_all([post1, post2])
        db.session.commit()
    
    # 访问首页
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    
    # 应显示文章标题
    assert "First Post" in html
    assert "Second Post" in html


def test_view_post_detail(client, app):
    """TC-POST-006: 查看文章详情"""
    with app.app_context():
        user = User(username="detailuser", email="detail@test.com")
        user.set_password("123456")
        db.session.add(user)
        db.session.commit()
        
        post = Post(title="Detail Post", body="Detail Content", user_id=user.id)
        db.session.add(post)
        db.session.commit()
        post_id = post.id
    
    resp = client.get(f"/blog/post/{post_id}")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    
    assert "Detail Post" in html
    assert "Detail Content" in html


def test_view_nonexistent_post_returns_404(client):
    """TC-POST-007: 查看不存在的文章返回 404"""
    resp = client.get("/blog/post/99999")
    assert resp.status_code == 404


def test_create_post_success(client, app):
    """TC-POST-001: 创建文章 - 正常流程"""
    # 创建并登录用户
    with app.app_context():
        user = User(username="createuser", email="create@test.com")
        user.set_password("123456")
        db.session.add(user)
        db.session.commit()
    
    r = client.get("/auth/login")
    token = _extract_csrf_token(r.get_data(as_text=True))
    client.post(
        "/auth/login",
        data={"csrf_token": token, "username": "createuser", "password": "123456"},
        follow_redirects=False,
    )
    
    # 创建文章
    r = client.get("/blog/create")
    token = _extract_csrf_token(r.get_data(as_text=True))
    
    resp = client.post(
        "/blog/create",
        data={"csrf_token": token, "title": "New Article", "body": "Article Content"},
        follow_redirects=False,
    )
    
    assert resp.status_code == 302
    
    # 验证文章已创建
    with app.app_context():
        post = Post.query.filter_by(title="New Article").first()
        assert post is not None
        assert post.body == "Article Content"


def test_edit_post_success(client, app):
    """TC-POST-008: 编辑文章 - 正常流程（作者）"""
    # 创建用户和文章
    with app.app_context():
        user = User(username="edituser", email="edit@test.com")
        user.set_password("123456")
        db.session.add(user)
        db.session.commit()
        
        post = Post(title="Original Title", body="Original Content", user_id=user.id)
        db.session.add(post)
        db.session.commit()
        post_id = post.id
    
    # 登录
    r = client.get("/auth/login")
    token = _extract_csrf_token(r.get_data(as_text=True))
    client.post(
        "/auth/login",
        data={"csrf_token": token, "username": "edituser", "password": "123456"},
        follow_redirects=False,
    )
    
    # 编辑文章
    r = client.get(f"/blog/post/{post_id}/edit")
    assert r.status_code == 200
    token = _extract_csrf_token(r.get_data(as_text=True))
    
    resp = client.post(
        f"/blog/post/{post_id}/edit",
        data={"csrf_token": token, "title": "Updated Title", "body": "Updated Content"},
        follow_redirects=False,
    )
    
    assert resp.status_code == 302
    
    # 验证文章已更新
    with app.app_context():
        post = Post.query.get(post_id)
        assert post.title == "Updated Title"
        assert post.body == "Updated Content"


def test_delete_post_success(client, app):
    """TC-POST-012: 删除文章 - 正常流程（作者）"""
    # 创建用户和文章
    with app.app_context():
        user = User(username="deluser", email="del@test.com")
        user.set_password("123456")
        db.session.add(user)
        db.session.commit()
        
        post = Post(title="To Be Deleted", body="Content", user_id=user.id)
        db.session.add(post)
        db.session.commit()
        post_id = post.id
    
    # 登录
    r = client.get("/auth/login")
    token = _extract_csrf_token(r.get_data(as_text=True))
    client.post(
        "/auth/login",
        data={"csrf_token": token, "username": "deluser", "password": "123456"},
        follow_redirects=False,
    )
    
    # 获取删除表单的 CSRF token
    r = client.get(f"/blog/post/{post_id}")
    token = _extract_csrf_token(r.get_data(as_text=True))
    
    # 删除文章
    resp = client.post(
        f"/blog/post/{post_id}/delete",
        data={"csrf_token": token},
        follow_redirects=False,
    )
    
    assert resp.status_code == 302
    
    # 验证文章已删除
    with app.app_context():
        post = Post.query.get(post_id)
        assert post is None


# ==================== 权限控制测试 ====================

def test_edit_other_user_post_returns_403(client, app):
    """TC-PERM-002: 非作者直接访问编辑 URL 返回 403"""
    # 创建作者和文章
    with app.app_context():
        author = User(username="author2", email="author2@test.com")
        author.set_password("123456")
        db.session.add(author)
        db.session.commit()
        
        post = Post(title="Author Post", body="Content", user_id=author.id)
        db.session.add(post)
        db.session.commit()
        post_id = post.id
    
    # 创建另一个用户
    r = client.get("/auth/register")
    token = _extract_csrf_token(r.get_data(as_text=True))
    client.post(
        "/auth/register",
        data={
            "csrf_token": token,
            "username": "other2",
            "email": "other2@test.com",
            "password": "123456",
            "password2": "123456",
        },
        follow_redirects=False,
    )
    
    # 登录其他用户
    r = client.get("/auth/login")
    token = _extract_csrf_token(r.get_data(as_text=True))
    client.post(
        "/auth/login",
        data={"csrf_token": token, "username": "other2", "password": "123456"},
        follow_redirects=False,
    )
    
    # 尝试编辑作者的文章
    resp = client.get(f"/blog/post/{post_id}/edit")
    assert resp.status_code == 403


def test_delete_other_user_post_returns_403(client, app):
    """TC-PERM-003: 非作者 POST 删除请求返回 403"""
    # 创建作者和文章
    with app.app_context():
        author = User(username="author3", email="author3@test.com")
        author.set_password("123456")
        db.session.add(author)
        db.session.commit()
        
        post = Post(title="Author Post 3", body="Content", user_id=author.id)
        db.session.add(post)
        db.session.commit()
        post_id = post.id
    
    # 创建并登录其他用户
    r = client.get("/auth/register")
    token = _extract_csrf_token(r.get_data(as_text=True))
    client.post(
        "/auth/register",
        data={
            "csrf_token": token,
            "username": "other3",
            "email": "other3@test.com",
            "password": "123456",
            "password2": "123456",
        },
        follow_redirects=False,
    )
    
    r = client.get("/auth/login")
    token = _extract_csrf_token(r.get_data(as_text=True))
    client.post(
        "/auth/login",
        data={"csrf_token": token, "username": "other3", "password": "123456"},
        follow_redirects=False,
    )
    
    # 尝试删除作者的文章（带 CSRF token）
    # 注意：非作者访问文章详情页时删除表单不渲染，需从其他页面获取 token
    r = client.get("/blog/create")
    token = _extract_csrf_token(r.get_data(as_text=True))
    
    resp = client.post(
        f"/blog/post/{post_id}/delete",
        data={"csrf_token": token},
        follow_redirects=False,
    )
    assert resp.status_code == 403
    
    # 验证文章仍存在
    with app.app_context():
        post = Post.query.get(post_id)
        assert post is not None
