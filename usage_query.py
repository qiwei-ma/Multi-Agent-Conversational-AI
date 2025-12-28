import sqlite3
from datetime import datetime, timedelta
import argparse  # 添加命令行参数解析

# 添加命令行参数解析
parser = argparse.ArgumentParser(description="用户消息统计查询工具")
parser.add_argument(
    "--sort",
    choices=["time", "count"],
    default="count",
    help="排序方式: time=按最新消息时间排序, count=按消息数量排序",
)
args = parser.parse_args()


def format_table(data, daily_counts=None):
    # 计算各列最大宽度，考虑中文字符占用两个宽度
    max_id = max(len(str(row[0])) for row in data)
    max_name = max(
        sum(2 if "\u4e00" <= char <= "\u9fff" else 1 for char in row[1]) for row in data
    )
    max_count = max(len(str(row[2])) for row in data)

    # 设置最小列宽
    max_id = max(max_id, 2) + 1  # ID列至少3个字符宽
    max_name = max(max_name, 4) + 2  # 姓名列至少6个字符宽
    max_count = max(max_count, 4) + 2  # 消息数列至少6个字符宽

    # 计算表头中文字符的宽度
    name_header = "姓名"
    name_header_width = sum(
        2 if "\u4e00" <= char <= "\u9fff" else 1 for char in name_header
    )
    name_header_padding = max_name - name_header_width

    count_header = "消息数"
    count_header_width = sum(
        2 if "\u4e00" <= char <= "\u9fff" else 1 for char in count_header
    )
    count_header_padding = max_count - count_header_width

    # 平均消息数表头
    avg_header = "日均"
    avg_header_width = sum(
        2 if "\u4e00" <= char <= "\u9fff" else 1 for char in avg_header
    )
    avg_width = 4  # 平均消息数列宽

    time_header = "最新消息时间"
    time_header_width = sum(
        2 if "\u4e00" <= char <= "\u9fff" else 1 for char in time_header
    )
    time_width = 13  # 固定宽度 (MM-DD HH:MM)

    # 设置每日消息数列宽
    day_width = 6  # 每日消息数列宽

    # 获取日期列表（从5月6日开始，但反转顺序）
    date_headers = []
    if daily_counts:
        start_date = datetime(2025, 5, 6)
        today = datetime.now()
        current_date = start_date
        while current_date <= today:
            date_headers.append(current_date.strftime("%m-%d"))
            current_date += timedelta(days=1)
        # 反转日期顺序，从最新到最旧
        date_headers.reverse()

    # 表头第一行
    header_first_line = f"╔{'═'*(max_id+2)}╦{'═'*(max_name+2)}╦{'═'*(max_count+2)}╦{'═'*(avg_width+2)}╦{'═'*(time_width+2)}"
    if daily_counts:
        for _ in date_headers:
            header_first_line += f"╦{'═'*(day_width+2)}"
    header_first_line += "╗"

    # 表头第二行
    header_second_line = (
        f"║ {'ID':^{max_id}} ║ {name_header}{' ' * name_header_padding} ║ "
        f"{count_header}{' ' * count_header_padding} ║ {avg_header} ║ "
        f"{time_header}{' ' * (time_width - time_header_width)} "
    )
    if daily_counts:
        for date in date_headers:
            header_second_line += f"║ {date:^{day_width}} "
    header_second_line += "║"

    # 表头分隔线
    header_separator = f"╠{'═'*(max_id+2)}╬{'═'*(max_name+2)}╬{'═'*(max_count+2)}╬{'═'*(avg_width+2)}╬{'═'*(time_width+2)}"
    if daily_counts:
        for _ in date_headers:
            header_separator += f"╬{'═'*(day_width+2)}"
    header_separator += "╣"

    # 打印表头
    print(header_first_line)
    print(header_second_line)
    print(header_separator)

    # 数据行
    for row in data:
        # 只显示月、日、时、分（不显示秒）
        time_str = row[3][5:16] if row[3] else "无记录"
        # 计算中文字符占用的额外空间
        name_display_width = sum(
            2 if "\u4e00" <= char <= "\u9fff" else 1 for char in row[1]
        )
        padding = max_name - name_display_width

        # 计算平均每日消息数
        user_id = row[0]
        avg_messages = 0
        if daily_counts and user_id in daily_counts:
            # 计算从5月6日到今天的总天数，而不是用户有消息的天数
            start_date = datetime(2025, 5, 6)
            today = datetime.now()
            total_days = (today - start_date).days + 1  # 包括开始和结束日

            # 计算总消息数
            total_messages = sum(daily_counts[user_id].values())
            # 计算平均值
            avg_messages = (
                round(total_messages / total_days, 1) if total_days > 0 else 0
            )

        line = (
            f"║ {str(row[0]):^{max_id}} ║ {row[1]}{' ' * padding} ║ "
            f"{str(row[2]):^{max_count}} ║ {str(avg_messages):^{avg_width}} ║ "
            f"{time_str:^{time_width}} "
        )

        # 添加每日消息数
        if daily_counts:
            user_id = row[0]
            for date_str in date_headers:
                # 转换日期格式为数据库中的格式 (MM-DD -> 2025-MM-DD)
                db_date = f"2025-{date_str}"
                count = daily_counts.get(user_id, {}).get(db_date, 0)
                line += f"║ {str(count):^{day_width}} "

        line += "║"
        print(line)

    # 表尾
    footer = f"╚{'═'*(max_id+2)}╩{'═'*(max_name+2)}╩{'═'*(max_count+2)}╩{'═'*(avg_width+2)}╩{'═'*(time_width+2)}"
    if daily_counts:
        for _ in date_headers:
            footer += f"╩{'═'*(day_width+2)}"
    footer += "╝"
    print(footer)


conn = sqlite3.connect("./user.db")
cursor = conn.cursor()

# 获取数据（只计算用户消息）
cursor.execute(
    """
    SELECT
        u.id,
        u.name,
        COUNT(m.id) as message_count,
        MAX(m.create_time) as latest_time
    FROM users u
    LEFT JOIN sessions s ON u.id = s.user_id
    LEFT JOIN messages m ON s.session_id = m.session_id AND m.type = 'user'
    GROUP BY u.id, u.name
"""
)

# 过滤数据
excluded_names = {
    "马启伟",
    "张君",
    "饶涵宇",
    "杨倩欣",
    "张宇",
    "庄严",
    "彭嘉辉",
    "莲叶何田田",
    "垚",
    "陈琴",
    "陈辉",
    "娄汉文",
    "张振远",
    "杨凯杰",
    "花花",
    "杨",
    "张泽",
    "杨莹",
    "王恺乐",
    "邹睿",
    "李金倩",
    "黄曼琪",
    "黄扬洽",
    "陈宇骏",
    "周子鸣",
    "曾嘉俊",
    "刘俊希",
    "余上游",
}
filtered_stats = [
    stat
    for stat in cursor.fetchall()
    if all("\u4e00" <= char <= "\u9fff" for char in stat[1])
    and stat[1] not in excluded_names
    and stat[2] > 0
]

# 根据命令行参数选择排序方式
if args.sort == "time":
    # 按时间排序
    filtered_stats.sort(key=lambda x: x[3] or "", reverse=True)
    sort_description = "按最新消息时间排序"
else:  # args.sort == 'count'
    # 按消息数排序
    filtered_stats.sort(key=lambda x: x[2], reverse=True)
    sort_description = "按消息数量排序"

# 获取每日消息数据（从指定日期开始）
start_date_str = "2025-05-15"  # 设置为5月15日

cursor.execute(
    """
    SELECT
        u.id,
        DATE(m.create_time) as message_date,
        COUNT(m.id) as daily_count
    FROM users u
    JOIN sessions s ON u.id = s.user_id
    JOIN messages m ON s.session_id = m.session_id
    WHERE m.type = 'user'
    AND DATE(m.create_time) >= '2025-05-06'
    GROUP BY u.id, DATE(m.create_time)
    ORDER BY u.id, message_date
"""
)

# 构建每日消息数据字典
daily_counts = {}
for row in cursor.fetchall():
    user_id, message_date, count = row
    if user_id not in daily_counts:
        daily_counts[user_id] = {}
    daily_counts[user_id][message_date] = count

# 打印表格
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(
    f"\n📊 用户消息统计表 ({sort_description}，不包含系统消息) 截至时间：{current_time}"
)
format_table(filtered_stats, daily_counts)

conn.close()
