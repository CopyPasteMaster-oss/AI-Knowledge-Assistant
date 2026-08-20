// app.js - 前端交互：上传文档 + 提问问答
const $ = (id) => document.getElementById(id);

// ---------- 上传文档 ----------
$("uploadBtn").addEventListener("click", async () => {
  const file = $("fileInput").files[0];
  if (!file) { $("uploadMsg").textContent = "请先选择文件"; return; }

  const formData = new FormData();
  formData.append("file", file);

  $("uploadMsg").textContent = "⏳ 上传解析中...";
  $("uploadBtn").disabled = true;
  try {
    const resp = await fetch("/upload", { method: "POST", body: formData });
    const data = await resp.json();
    $("uploadMsg").textContent = data.ok
      ? `✅ 入库成功：${data.chunks} 个片段（${data.filename}）`
      : `❌ ${data.error}`;
  } catch (e) {
    $("uploadMsg").textContent = "❌ 请求失败，请确认服务已启动";
  } finally {
    $("uploadBtn").disabled = false;
  }
});

// ---------- 提问 ----------
$("sendBtn").addEventListener("click", sendQuestion);
$("questionInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendQuestion();
});

async function sendQuestion() {
  const question = $("questionInput").value.trim();
  if (!question) return;

  addMessage("user", question);
  $("questionInput").value = "";
  addMessage("bot", "🤔 思考中...");

  try {
    const resp = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await resp.json();
    updateLastBot(data.answer || `❌ ${data.error}`);
  } catch (e) {
    updateLastBot("❌ 请求失败，请确认服务已启动");
  }
}

// ---------- 消息渲染 ----------
function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.textContent = text;
  $("messages").appendChild(div);
  $("messages").scrollTop = $("messages").scrollHeight;
}

function updateLastBot(text) {
  const msgs = $("messages").children;
  if (msgs.length > 0) msgs[msgs.length - 1].textContent = text;
}