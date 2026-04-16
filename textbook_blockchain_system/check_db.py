import sqlite3

# 连接到数据库
conn = sqlite3.connect('textbook_trade.db')
cursor = conn.cursor()

# 查看所有表
print("数据库中的表:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")

# 查看用户表
print("\n用户表内容:")
cursor.execute("SELECT * FROM users;")
users = cursor.fetchall()
for user in users:
    print(user)

# 查看教材元数据表
print("\n教材元数据表内容:")
cursor.execute("SELECT * FROM textbook_metadata;")
textbooks = cursor.fetchall()
for textbook in textbooks:
    print(textbook)

# 查看交易表
print("\n交易表内容:")
cursor.execute("SELECT * FROM transactions;")
transactions = cursor.fetchall()
for transaction in transactions:
    print(transaction)

# 关闭连接
conn.close()
