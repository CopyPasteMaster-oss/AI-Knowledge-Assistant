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

  // 收集最近几轮对话历史（多轮上下文）
  const history = [];
  const msgs = $("messages").querySelectorAll(".message");
  for (const m of msgs) {
    const text = m.textContent.replace(/📎 依据来源：.*$/s, "").trim();
    if (!text) continue;
    history.push(m.classList.contains("user")
      ? { question: text }
      : { answer: text });
  }

  try {
    const resp = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, history: history.slice(-6) }),
    });
    const data = await resp.json();
    renderBotAnswer(data);
  } catch (e) {
    updateLastBot("❌ 请求失败，请确认服务已启动");
  }
}

function renderBotAnswer(data) {
  const msg = $("messages").lastElementChild;
  msg.textContent = data.answer || `❌ ${data.error}`;
  if (data.sources && data.sources.length) {
    const src = document.createElement("div");
    src.className = "sources";
    src.textContent = "📎 依据来源：" + data.sources.map((s) => s.text).join(" ｜ ");
    msg.appendChild(src);
  }
  $("messages").scrollTop = $("messages").scrollHeight;
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