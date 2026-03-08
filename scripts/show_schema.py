"""显示数据库建表语句"""
import sqlite3
import os

# 获取项目根目录
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(current_dir, 'instance', 'blog.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('=== 数据库建表语句 ===\n')
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
for name, sql in cursor.fetchall():
    print(f'-- 表名: {name}')
    print(sql)
    print()

conn.close()
