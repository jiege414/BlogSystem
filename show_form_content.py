"""显示数据库完整内容（格式化输出）"""
import sqlite3

def print_table(title, headers, rows):
    """格式化打印表格"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)
    
    if not rows:
        print("  (暂无数据)")
        return
    
    # 计算每列最大宽度
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            cell_str = str(cell) if cell is not None else "NULL"
            col_widths[i] = max(col_widths[i], min(len(cell_str), 50))  # 最多显示50字符
    
    # 打印表头
    header_line = "  |  ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(f"  {header_line}")
    print("  " + "-" * (len(header_line) + 4))
    
    # 打印数据行
    for row in rows:
        formatted_row = []
        for i, cell in enumerate(row):
            cell_str = str(cell) if cell is not None else "NULL"
            # 截断过长的内容
            if len(cell_str) > 50:
                cell_str = cell_str[:47] + "..."
            formatted_row.append(cell_str.ljust(col_widths[i]))
        print(f"  {'  |  '.join(formatted_row)}")
    
    print(f"  共 {len(rows)} 条记录")


# 连接数据库
conn = sqlite3.connect('instance/blog.db')
cursor = conn.cursor()

# 获取所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print("="*60)
print("  数据库: instance/blog.db")
print(f"  包含表: {', '.join(t[0] for t in tables)}")

# 查看user表
cursor.execute('SELECT id, username, email, password_hash FROM user;')
rows = cursor.fetchall()
print_table("USER 表", ["ID", "用户名", "邮箱", "密码哈希"], rows)

# 查看post表
cursor.execute('SELECT id, title, body, timestamp, user_id FROM post;')
rows = cursor.fetchall()
print_table("POST 表", ["ID", "标题", "内容", "发布时间", "作者ID"], rows)

conn.close()
print(f"\n{'='*60}")
print("  查询完成")
print('='*60)
