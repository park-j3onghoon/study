// Synchronous chat (P3). SSE streaming will replace this in P4.
import { chat as chatApi } from "/js/api.js";

let messagesEl, formEl, inputEl, modelEl, effortEl, sendBtn;
let onAssistantResponse = null;
const history = []; // [{role: "user", content: "..."}, {role: "assistant", content: "..."}]

export function init(opts) {
  messagesEl = document.querySelector(opts.messagesSelector);
  formEl = document.querySelector(opts.formSelector);
  inputEl = document.querySelector(opts.inputSelector);
  modelEl = document.querySelector(opts.modelSelector);
  effortEl = document.querySelector(opts.effortSelector);
  sendBtn = formEl.querySelector("button[type=submit]");
  onAssistantResponse = opts.onAssistantResponse || null;

  formEl.addEventListener("submit", submit);
  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      submit(e);
    }
  });
}

async function submit(e) {
  e.preventDefault();
  const text = inputEl.value.trim();
  if (!text) return;
  appendMessage("user", text);
  history.push({ role: "user", content: text });
  inputEl.value = "";
  setSending(true);
  try {
    const resp = await chatApi({
      messages: history,
      model: modelEl.value,
      thinkingBudget: parseInt(effortEl.value, 10),
    });
    const textBlocks = (resp.content || []).filter((b) => b.type === "text");
    const assistantText = textBlocks.map((b) => b.text).join("\n").trim();
    if (assistantText) {
      appendMessage("assistant", assistantText);
      history.push({ role: "assistant", content: assistantText });
    }
    const toolsUsed = resp.tools_used || [];
    if (toolsUsed.length > 0) {
      appendMessage("tool", `🔧 도구 사용: ${toolsUsed.join(", ")}`);
    }
    if (onAssistantResponse) onAssistantResponse(resp);
  } catch (err) {
    appendMessage("error", `Error: ${err.message}`);
  } finally {
    setSending(false);
  }
}

function setSending(isSending) {
  sendBtn.disabled = isSending;
  sendBtn.textContent = isSending ? "응답 중…" : "보내기";
}

function appendMessage(role, text) {
  const div = document.createElement("div");
  div.className = `chat-msg ${role}`;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}
