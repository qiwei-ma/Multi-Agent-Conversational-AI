import whisper
import re
from pydub import AudioSegment
import io
import tempfile

def transcribe_audio(audio_bytes: bytes) -> list:
    """
    使用 Whisper 转录音频字节数据，返回包含文本和时间戳的段落列表。
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
        temp_audio_file_path = temp_audio_file.name
        # 将 MP3 转换为 WAV
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        audio_segment.export(temp_audio_file_path, format="wav")

    try:
        # 使用 Whisper 转录语音
        model = whisper.load_model("base")
        result = model.transcribe(temp_audio_file_path, word_timestamps=True)
        
        # 提取所有段落及其时间戳
        segments = result['segments']
        print("识别的段落及其时间戳：")
        for segment in segments:
            print(f"段落文本: {segment['text']}, 截止时间: {segment['end']}")
        
        return segments
    finally:
        # 确保临时文件被删除
        import os
        os.remove(temp_audio_file_path)

def filter_english_audio(audio_bytes: bytes) -> bytes:
    """
    接收原始音频字节数据，识别英文语音部分，并返回只保留英文的 MP3 格式音频字节。
    """
    # 转录音频并获取段落列表
    segments = transcribe_audio(audio_bytes)

    # 提取英文段落及其起止时间
    english_segments = []
    for segment in segments:
        if re.search(r'[a-zA-Z]', segment['text']):
            english_segments.append((segment['start'], segment['end']))

    # 加载原始音频为 pydub 对象
    original_audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
    english_audio = AudioSegment.empty()
    for start, end in english_segments:
        start_ms = int(start * 1000)
        end_ms = int(end * 1000)
        english_audio += original_audio[start_ms:end_ms]

    # 导出为 MP3 字节流
    mp3_buffer = io.BytesIO()
    english_audio.export(mp3_buffer, format="mp3")
    return mp3_buffer.getvalue()

def get_transcribed_text(audio_bytes: bytes) -> str:
    """
    使用 transcribe_audio 函数转录音频，并返回拼接后的完整文本。
    """
    segments = transcribe_audio(audio_bytes)
    transcribed_text = " ".join(segment['text'] for segment in segments)
    return transcribed_text

if __name__ == "__main__":
    with open("./testaudio/test3.mp3", "rb") as f:
        audio_bytes = f.read()
    res = filter_english_audio(audio_bytes=audio_bytes)

    # 获取转录的完整文本
    transcribed_text = get_transcribed_text(audio_bytes)
    print("完整转录文本：")
    print(transcribed_text)

    with open("./testaudio/english_only_test3.mp3", "wb") as f:
        f.write(res)