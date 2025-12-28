import re

from models import User, Post
from extensions import db


def _extract_csrf_token(html: str) -> str:
    # 匹配：name="csrf_token" type="hidden" value="..."
    m = re.search(r'name="csrf_token".*?value="([^"]+)"', html, re.S)
    assert m, "CSRF token not found in form"
    return m.group(1)


def _register_and_login(client, username="u1", email="u1@test.com", password="123456"):
    # 注册（需要 CSRF）
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

    # 登录（需要 CSRF）
    r = client.get("/auth/login")
    token = _extract_csrf_token(r.get_data(as_text=True))
    resp = client.post(
        "/auth/login",
        data={"csrf_token": token, "username": username, "password": password},
        follow_redirects=False,
    )
    return resp


def test_create_requires_login_redirects(client):
    resp = client.get("/blog/create", follow_redirects=False)
    # Flask-Login 默认是 302 到 /auth/login?next=...
    assert resp.status_code in (301, 302)
    assert "/auth/login" in resp.headers.get("Location", "")


def test_edit_forbidden_for_non_author(client, app):
    # 先在数据库里造一个作者和一篇文章
    with app.app_context():
        author = User(username="author", email="a@test.com")
        author.set_password("123456")
        db.session.add(author)
        db.session.commit()

        post = Post(title="t", body="b", user_id=author.id)
        db.session.add(post)
        db.session.commit()
        post_id = post.id

    # 再登录另一个用户
    _register_and_login(client, username="other", email="o@test.com", password="123456")

    # 访问编辑页应 403
    resp = client.get(f"/blog/post/{post_id}/edit", follow_redirects=False)
    assert resp.status_code == 403