"""显示数据库建表语句"""
import sqlite3

conn = sqlite3.connect('instance/blog.db')
cursor = conn.cursor()

print('=== 数据库建表语句 ===\n')
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
for name, sql in cursor.fetchall():
    print(f'-- 表名: {name}')
    print(sql)
    print()

conn.close()
