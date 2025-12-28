import logging
import os
import sys
import subprocess

# 设置libx264相关的日志级别为CRITICAL (最高级别)
logging.getLogger('libx264').setLevel(logging.CRITICAL)

# 全局设置日志级别为ERROR
logging.basicConfig(level=logging.ERROR)

# 自定义logger
logger = logging.getLogger('logger')
logger.setLevel(logging.ERROR)  # 只显示ERROR及以上级别的日志

# 重定向标准错误输出到/dev/null或NUL
if os.name == 'nt':  # Windows
    sys.stderr = open('NUL', 'w')
else:  # Unix/Linux
    sys.stderr = open('/dev/null', 'w')

# 创建一个空的处理器，不输出任何内容
class NullHandler(logging.Handler):
    def emit(self, record):
        pass

# 添加空处理器到根logger
logging.getLogger().addHandler(NullHandler())
# 移除所有其他处理器
for handler in logging.getLogger().handlers[:]:
    if not isinstance(handler, NullHandler):
        logging.getLogger().removeHandler(handler)

# 特别处理libx264的日志
libx264_logger = logging.getLogger('libx264')
for handler in libx264_logger.handlers[:]:
    libx264_logger.removeHandler(handler)
libx264_logger.addHandler(NullHandler())
libx264_logger.propagate = False  # 阻止日志传播到父logger

# 修改subprocess.Popen以默认重定向stderr
original_popen = subprocess.Popen

def silent_popen(*args, **kwargs):
    # 如果没有指定stderr，则重定向到DEVNULL
    if 'stderr' not in kwargs:
        kwargs['stderr'] = subprocess.DEVNULL
    return original_popen(*args, **kwargs)

# 替换原始的Popen
subprocess.Popen = silent_popen

# 确保FFmpeg命令中包含静默选项
def patch_ffmpeg_command(cmd):
    """
    修补FFmpeg命令以添加静默选项
    """
    if isinstance(cmd, list) and 'ffmpeg' in cmd[0]:
        # 检查是否已经有loglevel参数
        has_loglevel = False
        for i, arg in enumerate(cmd):
            if arg in ['-loglevel', '-v'] and i + 1 < len(cmd):
                has_loglevel = True
                break
        
        if not has_loglevel:
            # 在输入参数之前插入loglevel参数
            for i, arg in enumerate(cmd):
                if arg == '-i':
                    cmd.insert(i, 'quiet')
                    cmd.insert(i, '-loglevel')
                    break
    return cmd

# 修补os.system调用
original_system = os.system

def silent_system(command):
    if 'ffmpeg' in command:
        # 对于字符串命令，添加-loglevel quiet
        if '-loglevel' not in command and '-v' not in command:
            command = command.replace('ffmpeg', 'ffmpeg -loglevel quiet')
    return original_system(command)

# 替换原始的system
os.system = silent_system
