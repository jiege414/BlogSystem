from app import create_app
from models import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='test01').first()
    if user:
        print(f"用户ID: {user.id}")
        print(f"用户名: {user.username}")
        print(f"邮箱: {user.email}")
        print(f"密码哈希: {user.password_hash}")
        print(f"哈希长度: {len(user.password_hash)}")
        print(f"是否为哈希: {user.password_hash.startswith('scrypt:')}")
    else:
        print("用户未找到")