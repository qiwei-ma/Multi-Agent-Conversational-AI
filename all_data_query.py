import sqlite3

conn = sqlite3.connect("./user.db")
cursor = conn.cursor()

# 获取所有表名
cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
""")
tables = cursor.fetchall()

for table in tables:
    table_name = table[0]
    print(f"\nTable: {table_name}")

    # 打印表结构
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    print(" ".join(column_names))

    # 查询表中的所有数据并动态添加消息条数和会话 ID
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    for row in rows:
        print(" ".join(map(str, row)), end=" ")
        if table_name == 'users':
            user_id = row[0]
            # 查询该用户的消息条数和会话 ID
            cursor.execute("""
                SELECT COUNT(m.id), GROUP_CONCAT(DISTINCT s.session_id)
                FROM messages m
                JOIN sessions s ON m.session_id = s.session_id
                WHERE s.user_id = ?
            """, (user_id,))
            message_info = cursor.fetchone()
            message_count = message_info[0] if message_info and message_info[0] is not None else 0
            session_ids = message_info[1] if message_info and message_info[1] is not None else ""
            print(f"消息总数: {message_count} [会话ID列表: {session_ids}]")
        else:
            print()

# # 查询 messages 表中的所有数据 (已注释掉)
# print(f"\nTable: messages")
# cursor.execute(f"PRAGMA table_info(messages)")
# columns = cursor.fetchall()
# column_names = [column[1] for column in columns]
# print(" ".join(column_names))
# cursor.execute(f"SELECT * FROM messages")
# messages = cursor.fetchall()
# for message in messages:
#     print(" ".join(map(str, message)))

conn.close()
