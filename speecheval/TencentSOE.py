"""
Generate signature for Tencent SOE API
"""
import hmac
import hashlib
import base64
import time
import uuid
import urllib.parse
import asyncio
import websockets
import json
import random
import os

from .audio_utils import filter_english_audio

APPID = os.getenv("TENCENT_APPID", "1301978135")  # 获取：https://console.cloud.tencent.cn/cam/capi
SECRET_ID = os.getenv("TENCENT_SECRET_ID")
SECRET_KEY = os.getenv("TENCENT_SECRET_KEY")


def generate_signature(params, secret_key):
    """
    生成签名
    """
    sorted_params = sorted(params.items())
    query_str = '&'.join(f"{k}={v}" for k, v in sorted_params)
    raw_str = f"soe.cloud.tencent.com/soe/api/{APPID}?{query_str}"
    signature = hmac.new(
        secret_key.encode(), raw_str.encode(), hashlib.sha1).digest()
    return urllib.parse.quote_plus(base64.b64encode(signature).decode())


def tensent_soe_response(audio_bytes: bytes = None, session_info: dict = None):
    """
    评估音频数据
    """
    timestamp = int(time.time())
    expired = timestamp + 3600
    nonce = random.randint(1, 9999999999)
    server_engine_type = "16k_en"
    voice_id = str(uuid.uuid4())
    voiice_format = 2 # 0:pam 1:wav 2:mp3 3:speex
    text_mode = 0
    # ref_text = ref_text
    eval_mode = 3 # 3: 自由说模式 2: 段落模式 1: 句子模式 0: 单词模式
    score_coeff = 4.0 # 评估苛刻指数 4.0:最严格 0.0:最宽松
    sentence_info_enabled = 1
    rec_mode = 0 # 识别模式: 0:实时识别 1：录音识别

    # 剔除其中的中文
    audio_bytes = filter_english_audio(audio_bytes)

    params = {
        "secretid": SECRET_ID,
        "timestamp": timestamp,
        "expired": expired,
        "nonce": nonce,
        "server_engine_type": server_engine_type,
        "voice_id": voice_id,
        "voice_format": voiice_format,
        "text_mode": text_mode,
        # "ref_text": ref_text,
        "eval_mode": eval_mode,
        "score_coeff": score_coeff,
        "sentence_info_enabled": sentence_info_enabled,
        "rec_mode": rec_mode
    }

    signature = generate_signature(params, SECRET_KEY)
    query = urllib.parse.urlencode(params)  
    ws_url = f"wss://soe.cloud.tencent.com/soe/api/{APPID}?{query}&signature={signature}"

    async def run_ws():
        """
        Run websocket connection
        """
        async with websockets.connect(ws_url, ping_interval=None) as ws:

            # 发送音频流（每 40ms 一个数据包）
            chunk_size = 1280  # 16k 采样率下每 40ms 对应 1280 字节
            for i in range(0, len(audio_bytes), chunk_size):
                audio_chunk = audio_bytes[i:i + chunk_size]
                await ws.send(audio_chunk)
                await asyncio.sleep(0.04)  # 每 40ms 发送一次音频数据

            # 发送结束帧
            await ws.send(json.dumps({"type": "end"}))

            # 接收评测结果
            results = []
            while True:
                resp = await ws.recv()
                data = json.loads(resp)

                # 只打印最后的结果，若需要实时反馈请修改此处
                if data.get("final", 0) == 1:
                    results.append(data)
                    break
            return results

    # 创建新的事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run_ws())
    finally:
        loop.close()

def test():
    with open("./testaudio/test3.mp3", "rb") as f:
        audio_bytes = f.read()
    res = tensent_soe_response(audio_bytes=audio_bytes)
    print(res)

if __name__ == "__main__":
    test()