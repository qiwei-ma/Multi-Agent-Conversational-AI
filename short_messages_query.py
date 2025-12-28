import sqlite3
from datetime import datetime, timedelta
import argparse
import re
from collections import defaultdict

# 添加命令行参数解析
parser = argparse.ArgumentParser(description="短消息统计查询工具")
parser.add_argument(
    "--min_length",
    type=int,
    default=20,
    help="最小消息长度，短于此长度的中文消息将被统计",
)
parser.add_argument(
    "--min_words",
    type=int,
    default=5,
    help="最小单词数量，少于此数量的英文消息将被统计",
)
parser.add_argument(
    "--limit",
    type=int,
    default=50,
    help="显示的消息数量限制",
)
args = parser.parse_args()

# 需要排除的用户名单
excluded_names = {
    "马启伟", "张君", "饶涵宇", "杨倩欣", "张宇", "庄严", "彭嘉辉", 
    "莲叶何田田", "垚", "陈琴", "陈辉", "娄汉文", "张振远", "杨凯杰", 
    "花花", "杨", "张泽", "杨莹", "王恺乐", "邹睿", "李金倩", 
    "黄曼琪", "黄扬洽", "陈宇骏", "周子鸣", "曾嘉俊", "刘俊希", "余上游",
    "1",
}

# 判断消息是否为短消息
def is_short_message(content):
    # 检查消息是否主要是英文
    if re.search(r'[a-zA-Z]', content) and not re.search(r'[\u4e00-\u9fff]', content):
        # 英文消息，计算单词数
        words = re.findall(r'\b\w+\b', content)
        return len(words) < args.min_words
    else:
        # 中文或混合消息，使用字符长度
        return len(content) < args.min_length

def format_table(data):
    # 计算各列最大宽度，考虑中文字符占用两个宽度
    max_id = max(len(str(row[0])) for row in data) if data else 2
    max_name = max(
        sum(2 if "\u4e00" <= char <= "\u9fff" else 1 for char in row[1]) for row in data
    ) if data else 4
    max_content = max(
        sum(2 if "\u4e00" <= char <= "\u9fff" else 1 for char in str(row[3])) for row in data
    ) if data else 10
    max_length = max(len(str(row[4])) for row in data) if data else 2
    max_time = max(len(str(row[5][:16])) for row in data) if data else 16  # 只取到分钟

    # 设置最小列宽
    max_id = max(max_id, 2) + 1  # ID列至少3个字符宽
    max_name = max(max_name, 4) + 1  # 姓名列至少5个字符宽
    max_content = min(max_content, 30) + 2  # 内容列最多32个字符宽
    max_length = max(max_length, 4) + 1  # 长度列至少5个字符宽
    max_time = max(max_time, 16) + 1  # 时间列至少17个字符宽（YYYY-MM-DD HH:MM）

    # 表头
    header = (
        f"╔{'═'*(max_id+2)}╦{'═'*(max_name+2)}╦{'═'*(max_content+2)}╦{'═'*(max_length+2)}╦{'═'*(max_time+2)}╗\n"
        f"║ {'ID':^{max_id}} ║ {'姓名':^{max_name}} ║ {'消息内容':^{max_content}} ║ {'长度':^{max_length}} ║ {'时间':^{max_time}} ║\n"
        f"╠{'═'*(max_id+2)}╬{'═'*(max_name+2)}╬{'═'*(max_content+2)}╬{'═'*(max_length+2)}╬{'═'*(max_time+2)}╣"
    )
    print(header)

    # 数据行
    for row in data:
        user_id, name, session_id, content, length, time = row
        
        # 截断过长的内容
        content_display_width = sum(
            2 if "\u4e00" <= char <= "\u9fff" else 1 for char in content
        )
        if content_display_width > max_content - 2:
            # 截断内容，确保显示宽度不超过最大宽度
            truncated_content = ""
            current_width = 0
            for char in content:
                char_width = 2 if "\u4e00" <= char <= "\u9fff" else 1
                if current_width + char_width + 3 <= max_content:  # 为"..."预留空间
                    truncated_content += char
                    current_width += char_width
                else:
                    break
            content = truncated_content + "..."
        
        # 只显示到分钟（不显示秒）
        time_display = time[:16]
        
        # 计算实际显示宽度并填充
        name_display_width = sum(
            2 if "\u4e00" <= char <= "\u9fff" else 1 for char in name
        )
        name_padding = max_name - name_display_width
        
        content_display_width = sum(
            2 if "\u4e00" <= char <= "\u9fff" else 1 for char in content
        )
        content_padding = max_content - content_display_width

        # 确保填充正确
        line = (
            f"║ {str(user_id):^{max_id}} ║ {name}{' ' * name_padding} ║ "
            f"{content}{' ' * content_padding} ║ {str(length):^{max_length}} ║ "
            f"{time_display:^{max_time}} ║"
        )
        print(line)

    # 表尾
    footer = f"╚{'═'*(max_id+2)}╩{'═'*(max_name+2)}╩{'═'*(max_content+2)}╩{'═'*(max_length+2)}╩{'═'*(max_time+2)}╝"
    print(footer)

def format_daily_stats_table(data):
    # 计算各列最大宽度
    max_date = max(len(row[0]) for row in data) if data else 10
    max_short_count = max(len(str(row[1])) for row in data) if data else 10
    max_total_count = max(len(str(row[2])) for row in data) if data else 10
    max_percentage = max(len(f"{row[1]/row[2]*100:.2f}%") for row in data) if data else 8

    # 设置最小列宽
    max_date = max(max_date, 10) + 1
    max_short_count = max(max_short_count, 8) + 1
    max_total_count = max(max_total_count, 8) + 1
    max_percentage = max(max_percentage, 8) + 1

    # 表头中文字符的宽度计算
    date_header = "日期"
    date_header_width = sum(2 if "\u4e00" <= char <= "\u9fff" else 1 for char in date_header)
    date_header_padding = max_date - date_header_width
    
    short_count_header = "短消息数"
    short_count_header_width = sum(2 if "\u4e00" <= char <= "\u9fff" else 1 for char in short_count_header)
    short_count_header_padding = max_short_count - short_count_header_width
    
    total_count_header = "总消息数"
    total_count_header_width = sum(2 if "\u4e00" <= char <= "\u9fff" else 1 for char in total_count_header)
    total_count_header_padding = max_total_count - total_count_header_width
    
    percentage_header = "占比"
    percentage_header_width = sum(2 if "\u4e00" <= char <= "\u9fff" else 1 for char in percentage_header)
    percentage_header_padding = max_percentage - percentage_header_width

    # 表头
    header = (
        f"╔{'═'*(max_date+2)}╦{'═'*(max_short_count+2)}╦{'═'*(max_total_count+2)}╦{'═'*(max_percentage+2)}╗\n"
        f"║ {date_header}{' ' * date_header_padding} ║ "
        f"{short_count_header}{' ' * short_count_header_padding} ║ "
        f"{total_count_header}{' ' * total_count_header_padding} ║ "
        f"{percentage_header}{' ' * percentage_header_padding} ║\n"
        f"╠{'═'*(max_date+2)}╬{'═'*(max_short_count+2)}╬{'═'*(max_total_count+2)}╬{'═'*(max_percentage+2)}╣"
    )
    print(header)

    # 数据行
    for row in data:
        date, short_count, total_count = row
        percentage = short_count / total_count * 100 if total_count > 0 else 0
        percentage_str = f"{percentage:.2f}%"

        line = (
            f"║ {date:^{max_date}} ║ {str(short_count):^{max_short_count}} ║ "
            f"{str(total_count):^{max_total_count}} ║ "
            f"{percentage_str:^{max_percentage}} ║"
        )
        print(line)

    # 表尾
    footer = f"╚{'═'*(max_date+2)}╩{'═'*(max_short_count+2)}╩{'═'*(max_total_count+2)}╩{'═'*(max_percentage+2)}╝"
    print(footer)

def format_user_stats_table(user_stats, date_range):
    # 计算各列最大宽度
    max_id = max(len(str(user_id)) for user_id in user_stats.keys()) if user_stats else 2
    max_name = max(
        sum(2 if "\u4e00" <= char <= "\u9fff" else 1 for char in stats["name"]) 
        for stats in user_stats.values()
    ) if user_stats else 4
    max_short_count = max(len(str(stats["short_total"])) for stats in user_stats.values()) if user_stats else 5
    max_total_count = max(len(str(stats["total"])) for stats in user_stats.values()) if user_stats else 5
    max_percentage = max(
        len(f"{stats['short_total']/stats['total']*100:.1f}%") 
        for stats in user_stats.values() if stats['total'] > 0
    ) if user_stats else 6
    
    # 设置最小列宽，减小间距
    max_id = max(max_id, 2)
    max_name = max(max_name, 4)
    max_short_count = max(max_short_count, 5)
    max_total_count = max(max_total_count, 5)
    max_percentage = max(max_percentage, 5)
    
    # 日期列宽度，减小为刚好能容纳"x/y"格式
    date_width = 7  # 每日短消息数/总消息数列宽
    
    # 表头第一行
    header_first_line = f"╔═{'═'*max_id}╦═{'═'*max_name}╦═{'═'*max_short_count}╦═{'═'*max_total_count}╦═{'═'*max_percentage}"
    for _ in date_range:
        header_first_line += f"╦═{'═'*date_width}"
    header_first_line += "╗"
    
    # 表头第二行 - 计算中文字符的宽度
    id_header = "ID"
    
    name_header = "姓名"
    name_header_width = sum(2 if "\u4e00" <= char <= "\u9fff" else 1 for char in name_header)
    name_header_padding = max_name - name_header_width
    
    short_count_header = "短消息"
    short_count_header_width = sum(2 if "\u4e00" <= char <= "\u9fff" else 1 for char in short_count_header)
    
    total_count_header = "总消息"
    total_count_header_width = sum(2 if "\u4e00" <= char <= "\u9fff" else 1 for char in total_count_header)
    
    percentage_header = "占比"
    percentage_header_width = sum(2 if "\u4e00" <= char <= "\u9fff" else 1 for char in percentage_header)
    
    # 修复表头对齐问题，确保与数据行对齐
    # 使用与数据行完全相同的格式化方法和空格数量
    header_second_line = f"║{id_header:^{max_id+1}}║ {name_header}{' ' * name_header_padding}║"
    
    # 确保短消息列与数据行对齐
    short_padding = (max_short_count - short_count_header_width) // 2
    header_second_line += f" {short_count_header}{' ' * short_padding}║"
    
    # 确保总消息列与数据行对齐
    total_padding = (max_total_count - total_count_header_width) // 2
    header_second_line += f" {total_count_header}{' ' * total_padding}║"
    
    # 确保占比列与数据行对齐
    percentage_padding = (max_percentage - percentage_header_width) // 2
    header_second_line += f" {percentage_header}{' ' * percentage_padding}"
    
    # 确保日期列与数据行对齐
    for date in date_range:
        date_str = date.strftime("%m-%d")
        header_second_line += f"║{date_str:^{date_width+1}}"
    header_second_line += "║"
    
    # 表头分隔线
    header_separator = f"╠═{'═'*max_id}╬═{'═'*max_name}╬═{'═'*max_short_count}╬═{'═'*max_total_count}╬═{'═'*max_percentage}"
    for _ in date_range:
        header_separator += f"╬═{'═'*date_width}"
    header_separator += "╣"
    
    # 打印表头
    print(header_first_line)
    print(header_second_line)
    print(header_separator)
    
    # 按短消息占比降序排序用户
    sorted_users = sorted(
        user_stats.items(), 
        key=lambda x: (x[1]['short_total'] / x[1]['total'] if x[1]['total'] > 0 else 0), 
        reverse=True
    )
    
    # 数据行
    for user_id, stats in sorted_users:
        name = stats["name"]
        short_total = stats["short_total"]
        total = stats["total"]
        percentage = short_total / total * 100 if total > 0 else 0
        percentage_str = f"{percentage:.1f}%"  # 减少小数位数
        
        # 计算中文字符占用的额外空间
        name_display_width = sum(2 if "\u4e00" <= char <= "\u9fff" else 1 for char in name)
        name_padding = max_name - name_display_width
        
        # 使用固定格式处理ID，确保单数和双数ID都对齐
        id_str = str(user_id)
        if len(id_str) == 1:
            id_display = f"{id_str} "  # 单数ID后加一个空格
        else:
            id_display = id_str
            
        line = (
            f"║{id_display:^{max_id+1}}║ {name}{' ' * name_padding}║ "
            f"{str(short_total):^{max_short_count}}║ {str(total):^{max_total_count}}║ "
            f"{percentage_str:^{max_percentage}}"
        )
        
        # 添加每日短消息数/总消息数
        for date in date_range:
            date_str = date.strftime("%Y-%m-%d")
            daily_short = stats["daily_short"].get(date_str, 0)
            daily_total = stats["daily_total"].get(date_str, 0)
            daily_display = f"{daily_short}/{daily_total}" if daily_total > 0 else "-"
            line += f"║{daily_display:^{date_width+1}}"
        
        line += "║"
        print(line)
    
    # 表尾
    footer = f"╚═{'═'*max_id}╩═{'═'*max_name}╩═{'═'*max_short_count}╩═{'═'*max_total_count}╩═{'═'*max_percentage}"
    for _ in date_range:
        footer += f"╩═{'═'*date_width}"
    footer += "╝"
    print(footer)

# 连接数据库
conn = sqlite3.connect("./user.db")
cursor = conn.cursor()

# 获取所有消息，只获取2025-05-06之后的数据
cursor.execute(
    """
    SELECT 
        u.name,
        DATE(m.create_time) as message_date,
        m.content,
        m.id,
        m.create_time,
        u.id,
        m.session_id
    FROM messages m
    JOIN sessions s ON m.session_id = s.session_id
    JOIN users u ON s.user_id = u.id
    WHERE m.type = 'user'
    AND u.name NOT IN ({})
    AND DATE(m.create_time) >= '2025-05-06'
    ORDER BY m.create_time DESC
    """.format(','.join(['?'] * len(excluded_names))),
    list(excluded_names)
)

all_messages = cursor.fetchall()

# 过滤并计算统计数据
english_pattern = re.compile(r'[a-zA-Z]')
chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
daily_stats_dict = {}
user_stats_dict = {}
short_messages = []

# 创建日期范围（从2025-05-06到今天）
start_date = datetime(2025, 5, 6).date()
end_date = datetime.now().date()
date_range = []
current_date = start_date
while current_date <= end_date:
    date_range.append(current_date)
    current_date += timedelta(days=1)
date_range.reverse()  # 从最新到最旧

for name, date, content, msg_id, time, user_id, session_id in all_messages:
    # 跳过含有英文字母的用户名
    if english_pattern.search(name):
        continue
    
    # 初始化日期统计
    if date not in daily_stats_dict:
        daily_stats_dict[date] = {"short": 0, "total": 0}
    
    # 初始化用户统计
    if user_id not in user_stats_dict:
        user_stats_dict[user_id] = {
            "name": name,
            "short_total": 0,
            "total": 0,
            "daily_short": defaultdict(int),
            "daily_total": defaultdict(int)
        }
    
    # 更新总消息计数
    daily_stats_dict[date]["total"] += 1
    user_stats_dict[user_id]["total"] += 1
    user_stats_dict[user_id]["daily_total"][date] += 1
    
    # 判断是否为短消息
    is_short = False
    
    # 检查消息是否主要是英文
    if english_pattern.search(content) and not chinese_pattern.search(content):
        # 英文消息，计算单词数
        words = re.findall(r'\b\w+\b', content)
        word_count = len(words)
        is_short = word_count < args.min_words
        length_display = word_count  # 显示单词数而不是字符长度
    else:
        # 中文或混合消息，使用字符长度
        is_short = len(content) < args.min_length
        length_display = len(content)
    
    if is_short:
        daily_stats_dict[date]["short"] += 1
        user_stats_dict[user_id]["short_total"] += 1
        user_stats_dict[user_id]["daily_short"][date] += 1
        # 为短消息列表添加所需的数据格式
        short_messages.append((user_id, name, session_id, content, length_display, time))

# 转换为列表并排序
daily_stats = [(date, stats["short"], stats["total"]) 
               for date, stats in daily_stats_dict.items()]
daily_stats.sort(reverse=True)  # 按日期降序排序

# 限制短消息显示数量
short_messages = short_messages[:args.limit]

# 计算总短消息数和总消息数
total_short_messages = sum(day[1] for day in daily_stats)
total_messages = sum(day[2] for day in daily_stats)

# 打印统计信息
current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
print(f"\n📊 短消息统计 截至时间：{current_time}")
print(f"中文消息: 长度小于{args.min_length}字符的消息")
print(f"英文消息: 少于{args.min_words}个单词的消息")
print(f"短消息总数: {total_short_messages} / {total_messages} ({total_short_messages/total_messages*100:.2f}%)")
print(f"统计时间范围: 2025-05-06 至今")

# 打印每日短消息统计表
print(f"\n每日短消息统计表 (共{len(daily_stats)}天):")
format_daily_stats_table(daily_stats)

# 打印用户短消息统计表
print(f"\n用户短消息统计表 (共{len(user_stats_dict)}人):")
format_user_stats_table(user_stats_dict, date_range)  # 显示所有日期

# 打印短消息详细表格
if short_messages:
    print(f"\n以下是最近的{len(short_messages)}条短消息:")
    format_table(short_messages)
else:
    print("\n没有找到符合条件的短消息。")

conn.close()
