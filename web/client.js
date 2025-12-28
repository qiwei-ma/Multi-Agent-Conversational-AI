var pc = null;
var renderVideo = null;
var canvas = null;
var ctx = null;

function init() {
    renderVideo = document.getElementById("video");
    canvas = document.getElementById("canvas");
    ctx = canvas.getContext("2d");
}

let fallbackTimer;

async function start() {
    console.log("Starting host-only connection attempt...");

    const configHostOnly = {
        sdpSemantics: "unified-plan",
        iceServers: [],
        iceTransportPolicy: "all",
        iceCandidatePoolSize: 0,
    };

    pc = new RTCPeerConnection(configHostOnly);

    pc.addEventListener("icecandidate", (event) => {
        if (event.candidate) {
            console.log("[Host-Only ICE] candidate:", event.candidate.candidate);
        }
    });

    pc.addEventListener("track", (evt) => {
        if (evt.track.kind === "video") {
            document.getElementById("video").srcObject = evt.streams[0];
        } else if (evt.track.kind === "audio") {
            document.getElementById("audio").srcObject = evt.streams[0];
        }
    });

    let hostConnectSucceeded = false;

    pc.addEventListener("iceconnectionstatechange", () => {
        console.log("ICE Connection State:", pc.iceConnectionState);
        if (pc.iceConnectionState === "connected" || pc.iceConnectionState === "completed") {
            hostConnectSucceeded = true;
            clearTimeout(fallbackTimer);
            console.log("Host-only connection successful!");
        }
    });

    await negotiate();

    fallbackTimer = setTimeout(() => {
        if (!hostConnectSucceeded) {
            console.warn("Host connection failed, falling back to STUN/TURN...");
            startWithStunTurn();
        }
    }, 3000); // 3秒超时
}

window.start = start;

async function startWithStunTurn() {
    console.log("Starting STUN/TURN connection...");

    const configFull = {
        sdpSemantics: "unified-plan",
        iceServers: [
            { urls: "stun:stun.l.google.com:19302" },
            {
                urls: [
                    "turn:47.121.115.79:3478?transport=udp",
                    "turn:47.121.115.79:3478?transport=tcp",
                ],
                username: "admin",
                credential: "03280328",
            },
        ],
        iceTransportPolicy: "all",
        iceCandidatePoolSize: 4,
    };

    pc = new RTCPeerConnection(configFull);

    pc.addEventListener("icecandidate", (event) => {
        if (event.candidate) {
            console.log("[Full ICE] candidate:", event.candidate.candidate);
        }
    });

    pc.addEventListener("track", (evt) => {
        if (evt.track.kind === "video") {
            document.getElementById("video").srcObject = evt.streams[0];
        } else if (evt.track.kind === "audio") {
            document.getElementById("audio").srcObject = evt.streams[0];
        }
    });

    await negotiate();
}

async function negotiate() {
    pc.addTransceiver("video", { direction: "recvonly" });
    pc.addTransceiver("audio", { direction: "recvonly" });

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    await new Promise((resolve) => {
        if (pc.iceGatheringState === "complete") {
            resolve();
        } else {
            pc.addEventListener("icegatheringstatechange", function checkState() {
                if (pc.iceGatheringState === "complete") {
                    pc.removeEventListener("icegatheringstatechange", checkState);
                    resolve();
                }
            });
        }
    });

    const localOffer = pc.localDescription;
    const response = await fetch("/offer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            sdp: localOffer.sdp,
            type: localOffer.type,
        }),
    });

    const answer = await response.json();
    document.getElementById("sessionid").value = answer.sessionid;
    await pc.setRemoteDescription(answer);
}

function stop() {
    // document.getElementById('stop').style.display = 'none';

    // close peer connection
    setTimeout(() => {
        pc.close();
    }, 500);
}

window.onbeforeunload = function (e) {
    setTimeout(() => {
        pc.close();
    }, 500);
    e = e || window.event;
    // 兼容IE8和Firefox 4之前的版本
    if (e) {
        e.returnValue = "关闭提示";
    }
    // Chrome, Safari, Firefox 4+, Opera 12+ , IE 9+
    return "关闭提示";
};

function processVideoStream(videoElement) {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    document.getElementById("media").appendChild(canvas);

    videoElement.addEventListener("loadedmetadata", function () {
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;

        const processFrame = () => {
            if (videoElement.paused || videoElement.ended) return;

            // 将当前帧绘制到 canvas
            ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const data = imageData.data;
            // debugger
            // 遍历像素，进行抠图
            for (let i = 0; i < data.length; i += 4) {
                const r = data[i]; // 红色通道
                const g = data[i + 1]; // 绿色通道
                const b = data[i + 2]; // 蓝色通道

                // 判断是否为背景（绿色范围）
                if (g > 100 && r < 80 && b < 80) {
                    // 将背景设置为透明
                    data[i + 3] = 0; // alpha 通道设为 0（透明）
                }
            }

            // 更新处理后的图像数据
            ctx.putImageData(imageData, 0, 0);
            // console.log(imageData.data); // 输出所有像素的 RGBA 数组
            // // 将处理后的帧输出到新的视频流
            // const stream = canvas.captureStream();
            // outputVideo.srcObject = stream;
            //
            // // 继续处理下一帧
            requestAnimationFrame(processFrame);
        };
        processFrame();
    });
}
