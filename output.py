from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Session, Message
from datetime import datetime

# 创建数据库连接
engine = create_engine('sqlite:///user.db')
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

# 查询所有用户
print("\n=== 用户列表 ===")
users = db_session.query(User).all()
for user in users:
    print(f"\n用户ID: {user.id}")
    print(f"手机号: {user.phone}")
    print(f"姓名: {user.name}")
    print(f"创建时间: {user.create_time}")
    print("-" * 50)
    sessions = db_session.query(Session).filter(Session.user_id == user.id).order_by(Session.create_time).all()
    for session in sessions:
        print(f"- 会话ID: {session.session_id}")
        print(f"- 用户ID: {session.user_id}")
        print(f"  创建时间: {session.create_time}")

        # 查询该会话的所有消息
        messages = db_session.query(Message).filter(Message.session_id == session.session_id).order_by(Message.create_time).all()
        print("  聊天记录:")
        for msg in messages:
            # 根据消息类型显示不同标识
            sender = "用户" if msg.type == "user" else "系统"
            print(f"    [{sender}] {msg.create_time}: {msg.content}")
        print("-" * 50)

db_session.close()