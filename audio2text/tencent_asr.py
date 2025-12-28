import requests
import json
import base64
import os
import io
from datetime import datetime, timezone
import hmac
import hashlib
from pydub import AudioSegment


def call_tencent_asr(audio_bytes):

    # 转换为 MP3
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
    mp3_io = io.BytesIO()
    audio.export(mp3_io, format="mp3")
    mp3_bytes = mp3_io.getvalue()

    # Base64 编码
    base64_audio = base64.b64encode(mp3_bytes).decode("utf-8")

    host = "asr.tencentcloudapi.com"
    url = "https://" + host
    action = "SentenceRecognition"
    version = "2019-06-14"
    region = "ap-shanghai"

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-TC-Version": version,
        "X-TC-Region": region,
        "X-TC-Action": action,
        "X-TC-Timestamp": str(int(datetime.now().timestamp())),
        "Host": host,
    }

    payload = {
        "UsrAudioKey": "test",
        "SubServiceType": 2,
        "ProjectId": 0,
        "EngSerViceType": "16k_zh-PY",
        "VoiceFormat": "mp3",
        "Data": base64_audio,  # 使用 Base64 编码的音频数据
        "SourceType": 1,
    }

    secret_id = os.getenv("TENCENT_SECRET_ID")
    secret_key = os.getenv("TENCENT_SECRET_KEY")

    def get_authorization():
        timestamp = headers["X-TC-Timestamp"]
        # Use timezone-aware datetime to avoid deprecation warning
        date = datetime.fromtimestamp(int(timestamp), tz=timezone.utc).strftime(
            "%Y-%m-%d"
        )
        service = "asr"
        credential_scope = f"{date}/{service}/tc3_request"

        # Step 1: Build canonical request
        http_request_method = "POST"
        canonical_uri = "/"
        canonical_querystring = ""

        # Include x-tc-action in canonical headers and signed headers
        canonical_headers = (
            "content-type:application/json; charset=utf-8\n"
            f"host:{host}\n"
            f"x-tc-action:{action.lower()}\n"
        )
        signed_headers = "content-type;host;x-tc-action"

        # Calculate hashed request payload
        payload_json = json.dumps(payload)
        hashed_request_payload = hashlib.sha256(
            payload_json.encode("utf-8")
        ).hexdigest()

        canonical_request = (
            f"{http_request_method}\n"
            f"{canonical_uri}\n"
            f"{canonical_querystring}\n"
            f"{canonical_headers}\n"
            f"{signed_headers}\n"
            f"{hashed_request_payload}"
        )

        # Step 2: Build string to sign
        algorithm = "TC3-HMAC-SHA256"
        string_to_sign = (
            f"{algorithm}\n"
            f"{timestamp}\n"
            f"{credential_scope}\n"
            f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
        )

        # Step 3: Calculate signature
        # Use binary format for all HMAC operations
        secret_date = hmac.new(
            f"TC3{secret_key}".encode("utf-8"), date.encode("utf-8"), hashlib.sha256
        ).digest()
        secret_service = hmac.new(
            secret_date, service.encode("utf-8"), hashlib.sha256
        ).digest()
        secret_signing = hmac.new(
            secret_service, "tc3_request".encode("utf-8"), hashlib.sha256
        ).digest()
        signature = hmac.new(
            secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        # Step 4: Build authorization
        authorization = (
            f"{algorithm} "
            f"Credential={secret_id}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )
        return authorization

    headers["Authorization"] = get_authorization()

    # 发送请求
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # 检查 HTTP 错误
        result = response.json()

        # 提取 Result 字段
        if "Response" in result and "Result" in result["Response"]:
            return result["Response"]["Result"]
        elif "Error" in result["Response"]:
            error = result["Response"]["Error"]
            code = error.get("Code", "UnknownCode")
            message = error.get("Message", "No message provided")
            request_id = result["Response"].get("RequestId", "No RequestId")
            return f"Error Code: {code}\nMessage: {message}\nRequestId: {request_id}"
        else:
            return "Error: Neither 'Result' nor 'Error' field found in response"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}"


if __name__ == "__main__":
    file_path = "test3.mp3"
    if not os.path.exists(file_path):
        print(f"Error: 音频文件 {file_path} 不存在")
    else:
        audio = AudioSegment.from_file(file_path, format="mp3")
        duration_ms = len(audio)  # 时长（毫秒）
        file_size = os.path.getsize(file_path)  # 文件大小（字节）

        # 检查时长（不超过 60 秒）
        if duration_ms > 60000:
            raise ValueError(f"音频时长 {duration_ms/1000}s 超过 60s 限制")

        # 检查文件大小（不超过 3MB）
        if file_size > 3 * 1024 * 1024:
            raise ValueError(f"文件大小 {file_size/1024/1024:.2f}MB 超过 3MB 限制")

        # 直接读取文件的二进制数据，而不是Base64编码
        with open(file_path, "rb") as f:
            audio_bytes = f.read()

        result_text = call_tencent_asr(audio_bytes)
        print("Extracted Result:", result_text)
