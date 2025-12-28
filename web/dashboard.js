$(document).ready(function () {
  $("#video-size-slider").on("input", function () {
    const value = $(this).val();
    $("#video").css("width", value + "%");
  });

  // 从 localStorage 获取消息记录
  let messages = JSON.parse(localStorage.getItem("chatMessages")) || [];

  // 显示消息
  displayMessages();

  // 添加聊天消息
  function addChatMessage(message, type = "user") {
    const messagesContainer = $("#chat-messages");
    const messageClass = type === "user" ? "user-message" : "system-message";
    let rereadButton = `
            <button class="btn-reread" title="" data-text="${message.replace(
      /"/g,
      "&quot;"
    )}" 
                style="margin-left: 2px; background: none; border: none; cursor: pointer; color: #007bff;">
                <span style="margin-right: 2px; font-size: 0.9em;">AI</span><i class="bi bi-volume-up-fill"></i>
            </button>`;
    if (type === "user") {
      rereadButton = `
            <button class="btn-reread" title="" data-text="${message.replace(
        /"/g,
        "&quot;"
      )}" 
                style="margin-left: 2px; background: none; border: none; cursor: pointer; color:rgb(255, 255, 255);">
                <span style="margin-right: 2px; font-size: 0.9em;">AI</span><i class="bi bi-volume-up-fill"></i>
            </button>`;
    }

    const messageElement = $(`
        <div class="asr-text ${messageClass}">
            ${message}${rereadButton}
        </div>
    `);

    messagesContainer.append(messageElement);
    messagesContainer.scrollTop(messagesContainer[0].scrollHeight);

    // 无需判断类型，直接给所有 btn-reread 绑定点击事件
    messageElement.find(".btn-reread").on("click", function () {
      const textToReread = $(this).data("text");
      requestReread(textToReread);
    });
  }

  // 发音评分结果彩色文本添加，文本对话则使用上述addChatMessage
  function addChatMessageColor(
    message,
    type = "user",
    accuracyData,
    audioBlob
  ) {
    const messagesContainer = $("#chat-messages");
    const messageClass = type === "system" ? "system-message" : "user-message";

    // 带空格保留的分词方法
    const wordSplitRegex = /(\s+)/;
    const messageParts = message.split(wordSplitRegex);

    const coloredMessage = messageParts
      .map((part) => {
        // 处理非空格内容
        if (!wordSplitRegex.test(part)) {
          const getWordColor = (word) => {
            const lowerWord = word.toLowerCase();
            const isHigh = accuracyData.highAccuracyWords.some(
              (w) => lowerWord === w.toLowerCase()
            );
            const isMedium = accuracyData.mediumAccuracyWords.some(
              (w) => lowerWord === w.toLowerCase()
            );
            const isLow = accuracyData.lowAccuracyWords.some(
              (w) => lowerWord === w.toLowerCase()
            );

            if (isHigh) return "high-accuracy-color";
            if (isMedium) return "medium-accuracy-color";
            if (isLow) return "low-accuracy-color";
            return "";
          };

          return `<span class="${getWordColor(part)}">${part}</span>`;
        }
        // 保留原始空格
        return part;
      })
      .join("");

    // 添加喇叭图标（仅在用户消息且有音频时显示）
    const audioPlayer =
      audioBlob && audioBlob instanceof Blob
        ? `<button class="audio-play-btn" title="播放录音">
                <i class="fa fa-volume-up" aria-hidden="true" style="font-size: 0.9em;"></i>
            </button>
            <audio class="audio-player" src="${URL.createObjectURL(
          audioBlob
        )}"></audio>`
        : "";

    const messageElement = $(`
            <div class="asr-text ${messageClass}">
                ${coloredMessage} ${audioPlayer}<br />
                <span style="font-size: 0.7em;">
                    <span style="color: ${accuracyData.suggestedScore > 80 ? '#7DDA58' : accuracyData.suggestedScore > 50 ? '#FFDE59' : '#FF4D4F'}">
                    Score: ${accuracyData.suggestedScore}</span> | 
                    Accuracy: ${accuracyData.pronAccuracy} | 
                    Fluency: ${accuracyData.pronFluency}
                    <button class="btn-reread" title="" data-text="${message.replace(/"/g, "&quot;")}" 
                        style="margin-left: 8px; background: none; border: none; cursor: pointer; color:rgb(255, 255, 255);">
                        <span style="margin-right: 2px; font-size: 0.9em;">AI</span><i class="bi bi-volume-up-fill"></i>
                    </button>
                </span>
            </div>
        `);

    messagesContainer.append(messageElement);
    messagesContainer.scrollTop(messagesContainer[0].scrollHeight);

    if (audioBlob) {
      messageElement.find(".audio-play-btn").on("click", function () {
        const audioElement = messageElement.find(".audio-player")[0];
        if (audioElement.paused) {
          audioElement.play();
          $(this).html('<i class="fas fa-pause"></i>');
        } else {
          audioElement.pause();
          audioElement.currentTime = 0;
          $(this).html('<i class="fas fa-volume-up"></i>');
        }
      });
    }

    messageElement.find(".btn-reread").on("click", function () {
      const textToReread = $(this).data("text");
      requestReread(textToReread);
    });
  }

  // 添加显示加载动画的函数
  function showChatLoading(type = "system") {
    const loadingElement = $(`
            <div class="chat-loading ${type}-loading">
                <div class="dots">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                </div>
            </div>
        `);
    $("#chat-messages").append(loadingElement);
    $("#chat-messages").scrollTop($("#chat-messages")[0].scrollHeight);
    return loadingElement;
  }

  // 添加评价结果
  function addEvalMessage(
    recognizedText,
    SuggestedScore,
    PronAccuracy,
    PronFluency,
    type = "eval"
  ) {
    const messagesContainer = $("#chat-messages");
    const messageClass = "eval-message";

    const messageElement = $(`
            <div class="asr-text ${messageClass}">
            <div class="eval-scores">
                Score: ${SuggestedScore} | 
                Accuracy: ${PronAccuracy} | 
                Fluency: ${PronFluency}
            </div>
                    <button class="btn-reread" title="" data-text="${recognizedText.replace(
      /"/g,
      "&quot;"
    )}" 
            style="margin-left: 4px; background: none; border: none; cursor: pointer; color: #007bff;">
            <span style="font-size: 0.9em;">AI</span><i class="bi bi-volume-up-fill"></i>
        </button>
        </div>
        `);

    messagesContainer.append(messageElement);
    messagesContainer.scrollTop(messagesContainer[0].scrollHeight);

    messageElement.find(".btn-reread").on("click", function () {
      const textToReread = $(this).data("text");
      requestReread(textToReread);
    });
  }

  function updateLastChatMessageColor(
    newMessage,
    HighAccuracyWords,
    MediumAccuracyWords,
    LowAccuracyWords
  ) {
    const messagesContainer = $("#chat-messages");
    const lastMessageElement = messagesContainer.find(".asr-text").last();

    if (lastMessageElement.length === 0) return;

    // 带空格保留的分词方法
    const wordSplitRegex = /(\s+)/;
    const messageParts = newMessage.split(wordSplitRegex);

    const coloredMessage = messageParts
      .map((part) => {
        if (!wordSplitRegex.test(part)) {
          const getWordColor = (word) => {
            const lowerWord = word.toLowerCase();
            const isHigh = HighAccuracyWords.some(
              (w) => lowerWord === w.toLowerCase()
            );
            const isMedium = MediumAccuracyWords.some(
              (w) => lowerWord === w.toLowerCase()
            );
            const isLow = LowAccuracyWords.some(
              (w) => lowerWord === w.toLowerCase()
            );

            if (isHigh) return "high-accuracy-color";
            if (isMedium) return "medium-accuracy-color";
            if (isLow) return "low-accuracy-color";
            return "";
          };

          return `<span class="${getWordColor(part)}">${part}</span>`;
        }
        return part;
      })
      .join("");

    lastMessageElement.html(coloredMessage);
  }

  // 发送重读请求
  function requestReread(text) {
    text = text.trim();
    if (!text.trim()) return;

    console.log("Requesting reread:", text);

    fetch("/human", {
      body: JSON.stringify({
        text: text,
        type: "echo",
        interrupt: true,
        sessionid: parseInt(document.getElementById("sessionid").value),
        user_id: localStorage.getItem("user_id"),
      }),
      headers: {
        "Content-Type": "application/json",
      },
      method: "POST",
    });
  }

  // 格式化时间
  function formatDate(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  }

  // 获取当前时间
  function getCurrentTime() {
    return formatDate(new Date());
  }

  // 显示消息
  function displayMessages() {
    if (localStorage.getItem("chatMessages") == null) {
      saveMessageToHistory("Hello, I'm Amy", "system");
    }

    messages.forEach((message) => {
      if (message.type == "eval") {
        addChatMessageColor(
          message.content,
          message.type,
          message.accuracyData,
          message.audioBlob
        );
      } else {
        addChatMessage(message.content, message.type);
      }
      $("#chat-message").val("");
    });
  }

  // 使用事件委托来处理按钮点击
  $("#clearHistoryBtn").on("click", function () {
    clearHistory();
    fetch("/clear", {
      body: JSON.stringify({
        text: "clear",
        sessionid: parseInt(document.getElementById("sessionid").value),
      }),
      headers: {
        "Content-Type": "application/json",
      },
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        localStorage.setItem("conversation_id", data.data);
      });
  });

  // 清空聊天记录
  function clearHistory() {
    if (confirm("确定要清空所有聊天记录吗？此操作不可撤销。")) {
      messages = [];
      localStorage.removeItem("chatMessages"); // 清空本地存储

      // 清空当前聊天界面
      $("#chat-messages").empty();
      // 只保留欢迎消息
      addChatMessage("Hello, I'm Amy", "system");
      $("#chat-message").val("");
      saveMessageToHistory("Hello, I'm Amy", "system");
    }
  }

  function saveMessageToHistory(message, type = "user") {
    const newMessage = {
      id: Date.now(), // 使用时间戳作为唯一ID
      timestamp: getCurrentTime(),
      content: message,
      type: type,
    };

    messages.push(newMessage);
    localStorage.setItem("chatMessages", JSON.stringify(messages)); // 保存到 localStorage
  }

  function saveMessageToEvalHistory(
    message,
    accuracyData,
    type = "eval",
    audioBlob
  ) {
    const newMessage = {
      id: Date.now(), // 使用时间戳作为唯一ID
      timestamp: getCurrentTime(),
      accuracyData: accuracyData,
      audioBlob: audioBlob instanceof Blob ? audioBlob : null,
      content: message,
      type: type,
    };

    messages.push(newMessage);
    localStorage.setItem("chatMessages", JSON.stringify(messages)); // 保存到 localStorage
  }

  // 聊天模式表单提交
  $("#chat-form").on("submit", function (e) {
    e.preventDefault();
    var message = $("#chat-message").val();
    if (!message.trim()) return;

    console.log("Sending chat message:", message);

    addChatMessage(message, "user");
    $("#chat-message").val("");
    saveMessageToHistory(message, "user"); // 保存用户消息到历史记录

    // 显示加载动画
    const userLoadingElement = showChatLoading("user");

    fetch("/human", {
      body: JSON.stringify({
        text: message,
        type: "chat",
        interrupt: true,
        sessionid: parseInt(document.getElementById("sessionid").value),
        user_id: localStorage.getItem("user_id"),
      }),
      headers: {
        "Content-Type": "application/json",
      },
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        // 移除加载动画
        userLoadingElement.remove();

        console.log("Replying chat message:", data.data);
        addChatMessage(data.data, "system");
        $("#chat-message").val("");
        localStorage.setItem("conversation_id", data.conversation_id);
        saveMessageToHistory(data.data, "system"); // 保存系统消息到历史记录
      });
  });

  // 添加回车键发送功能
  $("#chat-message").on("keydown", function (e) {
    if (e.keyCode === 13 && !e.shiftKey) {
      e.preventDefault(); // 防止在文本框中插入换行
      $("#chat-form").submit(); // 触发表单提交
    }
  });

  // 录制功能
  $("#btn_start_record").click(function () {
    console.log("Starting recording...");
    fetch("/record", {
      body: JSON.stringify({
        type: "start_record",
        sessionid: parseInt(document.getElementById("sessionid").value),
      }),
      headers: {
        "Content-Type": "application/json",
      },
      method: "POST",
    })
      .then(function (response) {
        if (response.ok) {
          console.log("Recording started.");
          $("#btn_start_record").prop("disabled", true);
          $("#btn_stop_record").prop("disabled", false);
          $("#recording-indicator").addClass("active");
        } else {
          console.error("Failed to start recording.");
        }
      })
      .catch(function (error) {
        console.error("Error:", error);
      });
  });

  $("#btn_stop_record").click(function () {
    console.log("Stopping recording...");
    fetch("/record", {
      body: JSON.stringify({
        type: "end_record",
        sessionid: parseInt(document.getElementById("sessionid").value),
      }),
      headers: {
        "Content-Type": "application/json",
      },
      method: "POST",
    })
      .then(function (response) {
        if (response.ok) {
          console.log("Recording stopped.");
          $("#btn_start_record").prop("disabled", false);
          $("#btn_stop_record").prop("disabled", true);
          $("#recording-indicator").removeClass("active");
        } else {
          console.error("Failed to stop recording.");
        }
      })
      .catch(function (error) {
        console.error("Error:", error);
      });
  });

  // 按住说话功能
  let mediaRecorder;
  let audioChunks = [];
  let isRecording = false;
  let recognizedText = "";
  let countdownInterval;
  let countdownTime = 59;

  // 按住说话按钮事件
  $("#voice-record-btn")
    .on("mousedown touchstart", function (e) {
      e.preventDefault();
      startRecording();
    })
    .on("mouseup mouseleave touchend", function () {
      if (isRecording) {
        stopRecording();
      }
    });

  $(document)
    .on("keydown", function (e) {
      var keyCode = e.keyCode || e.which;
      if (keyCode === 32) {
        // 检查是否聚焦在输入框内
        if (!$("#chat-message").is(":focus")) {
          e.preventDefault();
          startRecording();
        }
      }
    })
    .on("keyup", function () {
      if (isRecording) {
        stopRecording();
      }
    });

  // 开始录音
  function startRecording() {
    if (isRecording) return;

    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then(function (stream) {
        audioChunks = [];
        mediaRecorder = new MediaRecorder(stream);

        // 录音数据处理
        mediaRecorder.ondataavailable = function (e) {
          if (e.data.size > 0) {
            audioChunks.push(e.data);
          }
        };

        mediaRecorder.start();
        isRecording = true;

        $("#voice-record-btn").addClass("recording-pulse");
        $("#voice-record-btn").css("background-color", "#dc3545");

        // 开始倒计时
        startCountdown();
      })
      .catch(function (error) {
        console.error("无法访问麦克风:", error);
        alert("无法访问麦克风，请检查浏览器权限设置。");
      });
  }

  function stopRecording() {
    if (!isRecording) return;

    mediaRecorder.stop();
    isRecording = false;

    // 停止所有音轨
    mediaRecorder.stream.getTracks().forEach((track) => track.stop());

    // 视觉反馈恢复
    $("#voice-record-btn").removeClass("recording-pulse");
    $("#voice-record-btn").css("background-color", "");

    // 停止倒计时
    stopCountdown();

    mediaRecorder.onstop = function () {
      if (!audioChunks || audioChunks.length === 0) {
        console.error("录音数据为空，无法发送 /audio2text");
        return;
      }

      // Calculate the duration from the audio chunks
      const blob = new Blob(audioChunks, { type: "audio/mp3" });
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const fileReader = new FileReader();

      fileReader.onload = function () {
        audioContext.decodeAudioData(fileReader.result, function (buffer) {
          const recordingTime = buffer.duration;

          // Check if recording time is less than 1 second
          if (recordingTime < 5) {
            alert("您的说话时间不足5秒");
            return;
          }
          console.log("recordingTime:", recordingTime);

          // Proceed with the rest of the logic
          const formData = new FormData();
          formData.append("audio", blob);
          formData.append(
            "sessionid",
            parseInt(document.getElementById("sessionid").value)
          );
          const userLoadingElement = showChatLoading("user");
          fetch("/audio2text", {
            method: "POST",
            body: formData,
          })
            .then((res) => {
              return res.json();
            })
            .then((data) => {
              if (data && data.code === 0 && typeof data.data === "string") {
                recognizedText = data.data.trim();
              } else {
                console.error("Error: Invalid response from /audio2text", data);
              }
              if (recognizedText) {
                // 获取录音、请求评估
                function speecheval() {
                  return new Promise((resolve, reject) => {
                    fetch("/speecheval", {
                      method: "POST",
                      body: formData,
                    })
                      .then((res) => res.json())
                      .then((data) => {
                        // 移除加载动画
                        userLoadingElement.remove();
                        console.log("发送聊天消息:", recognizedText);
                        try {
                          const accuracyData = {
                            highAccuracyWords: data.data["HighAccuracyWords"] || [],
                            mediumAccuracyWords: data.data["MediumAccuracyWords"] || [],
                            lowAccuracyWords: data.data["LowAccuracyWords"] || [],
                            suggestedScore:
                              Math.round(data.data["TotalSuggestedScore"] || 0),
                            pronAccuracy: Math.round(data.data["TotalPronAccuracy"] || 0),
                            pronFluency: Math.round((data.data["TotalPronFluency"] || 0) * 100),
                          };
                          addChatMessageColor(
                            recognizedText,
                            "user",
                            accuracyData,
                            blob
                          );
                          $("#chat-message").val("");
                          saveMessageToEvalHistory(
                            recognizedText,
                            accuracyData,
                            "eval",
                            blob
                          );
                        } catch (err) {
                          console.error("处理评估数据时出错:", err);
                        }
                        resolve(); // 无论如何都resolve
                      })
                      .catch((error) => {
                        // 发生错误时也要移除加载动画
                        userLoadingElement.remove();
                        console.error("评估失败:", error);
                        resolve(); // 错误情况下也要resolve，确保human()会被调用
                      });
                  });
                }
                // 发送识别的文本
                function humanProcess() {
                  return fetch("/preprocess", {
                    body: JSON.stringify({
                      text: recognizedText,
                      type: "chat",
                      interrupt: true,
                      sessionid: parseInt(
                        document.getElementById("sessionid").value
                      ),
                    }),
                    headers: {
                      "Content-Type": "application/json",
                    },
                    method: "POST",
                  })
                    .then((res) => res.json())
                    .then((preprocessData) => {
                      const processedText = preprocessData.data;
                      console.log("preprocess chat message:", processedText);

                      return fetch("/human", {
                        body: JSON.stringify({
                          text: processedText,
                          type: "chat",
                          interrupt: true,
                          sessionid: parseInt(
                            document.getElementById("sessionid").value
                          ),
                          user_id: localStorage.getItem("user_id"),
                        }),
                        headers: {
                          "Content-Type": "application/json",
                        },
                        method: "POST",
                      });
                    })
                    .then((res) => res.json());
                }


                // Execute both functions and get their promises
                const speechEvalPromise = speecheval();
                const humanPromise = humanProcess();

                // Wait for speecheval to complete before showing system loading animation
                speechEvalPromise.then(() => {
                  const systemLoadingElement = showChatLoading("system");

                  // Wait for human processing to complete, then remove loading animation and save message
                  humanPromise.then((humanData) => {
                    systemLoadingElement.remove();
                    console.log("回复聊天消息:", humanData.data);
                    addChatMessage(humanData.data, "system");
                    $("#chat-message").val("");
                    localStorage.setItem(
                      "conversation_id",
                      humanData.conversation_id
                    );
                    saveMessageToHistory(humanData.data, "system");
                  }).catch((error) => {
                    systemLoadingElement.remove();
                    console.error("Error in human():", error);
                  });
                });
              }
            })
            .catch((error) => {
              console.error("Error fetching /audio2text:", error);
            });
        });
      };

      fileReader.readAsArrayBuffer(blob);
    };
  }

  // WebRTC 相关功能
  if (typeof window.onWebRTCConnected === "function") {
    const originalOnConnected = window.onWebRTCConnected;
    window.onWebRTCConnected = function () {
      updateConnectionStatus("connected");
      if (originalOnConnected) originalOnConnected();
    };
  } else {
    window.onWebRTCConnected = function () {
      updateConnectionStatus("connected");
    };
  }

  // 当连接断开时更新状态
  if (typeof window.onWebRTCDisconnected === "function") {
    const originalOnDisconnected = window.onWebRTCDisconnected;
    window.onWebRTCDisconnected = function () {
      updateConnectionStatus("disconnected");
      if (originalOnDisconnected) originalOnDisconnected();
    };
  } else {
    window.onWebRTCDisconnected = function () {
      updateConnectionStatus("disconnected");
    };
  }

  // SRS WebRTC播放功能
  var sdk = null; // 全局处理器，用于在重新发布时进行清理

  function startPlay() {
    // 关闭之前的连接
    if (sdk) {
      sdk.close();
    }

    sdk = new SrsRtcWhipWhepAsync();
    $("#video").prop("srcObject", sdk.stream);

    var host = window.location.hostname;
    var url =
      "http://" + host + ":1985/rtc/v1/whep/?app=live&stream=livestream";

    sdk
      .play(url)
      .then(function (session) {
        console.log("WebRTC播放已启动，会话ID:", session.sessionid);
      })
      .catch(function (reason) {
        sdk.close();
        console.error("WebRTC播放失败:", reason);
      });
  }

  // 添加倒计时函数
  function startCountdown() {
    // 重置倒计时
    countdownTime = 59;
    $("#countdown-timer").text(countdownTime);
    $("#countdown-timer").addClass("active");

    // 设置倒计时间隔
    countdownInterval = setInterval(function () {
      countdownTime--;
      $("#countdown-timer").text(countdownTime);

      // 当倒计时到0时，自动停止录音
      if (countdownTime <= 0) {
        stopRecording();
      }
    }, 1000);
  }

  // 添加停止倒计时函数
  function stopCountdown() {
    clearInterval(countdownInterval);
    $("#countdown-timer").removeClass("active");
  }
});
