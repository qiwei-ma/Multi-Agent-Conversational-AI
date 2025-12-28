<div align="center">

# Multi-Agent-Spoken

</div>

## TODO
- [x] Coze API
- [x] 评分系统
- [x] 对话展示
- [x] 输入检测
- [x] 模型
- [x] 音色
- [x] 界面美化
- [x] 手机适配
- [x] 部署

# Start 
## Linux
1. 环境配置
```
conda create -n nerfstream python=3.10
conda activate nerfstream
# If the cuda version is not 11.3 (confirm the version by running nvidia-smi), install the corresponding version of pytorch according to <https://pytorch.org/get-started/previous-versions/> 
conda install pytorch==1.12.1 torchvision==0.13.1 cudatoolkit=11.3 -c pytorch
pip install -r requirements.txt
# If you need to train the ernerf model, install the following libraries
# pip install "git+https://github.com/facebookresearch/pytorch3d.git"
# pip install tensorflow-gpu==2.8.0
# pip install --upgrade "protobuf<=3.20.1"
```
2. 端口开放
```
firewall-cmd --zone=public ---permanent -add-port=8010/tcp
firewall-cmd --zone=public ---permanent -add-port=1-65535/udp
```

3. 运行
```
python app.py --transport webrtc --model wav2lip --avatar_id wav2lip256_avatar5 --tts tencent --REF_FILE 101006 --customvideo_config data/custom_config.json
python app.py --transport webrtc --model wav2lip --avatar_id wav2lip256_avatar5 --tts tencent --REF_FILE 501009 --customvideo_config data/custom_config.json (大模型音色字数限制：100000)
```

4. 查看
```
http://127.0.0.1:8010/login.html
http://127.0.0.1:8010/dashboard.html
```

5. 视频编排
- 素材生成
```
ffmpeg -i xxx.mp4 -vf fps=25 -qmin 1 -q:v 1 -start_number 0 data/customvideo/image/%08d.png
# 生成空音频
ffmpeg -f lavfi -i anullsrc=channel_layout=mono:sample_rate=16000 -t 10 -acodec pcm_s16le data\customvideo\audio.wav
```

# Acknowledgements
https://github.com/lipku/LiveTalking 
