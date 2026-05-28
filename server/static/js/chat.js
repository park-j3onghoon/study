// SSE-streaming chat. Wires assistant text/thinking/tool events into the DOM live.
// conversation_id is persisted in localStorage so chat continues across reloads.
import { chatStream, createConversation, getConversation, listModels } from "/js/api.js";

const LS_KEY = "study.conversation_id";

let messagesEl, formEl, inputEl, modelEl, effortEl, sendBtn;
let onAssistantResponse = null;
let conversationId = null;
const history = []; // [{role:"user"|"assistant", content:"..."}, ...]

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

  populateModels();
  restoreConversation();
}

async function populateModels() {
  try {
    const models = await listModels();
    if (!models.length) return;
    modelEl.innerHTML = "";
    for (const m of models) {
      const opt = document.createElement("option");
      opt.value = m.id;
      opt.textContent = m.display_name;
      modelEl.appendChild(opt);
    }
    // Server already orders best-family first → first option is the default.
    modelEl.value = models[0].id;
  } catch (err) {
    // 503 등은 그냥 무시 — index.html의 기본 옵션이 fallback으로 남는다.
    console.warn("listModels failed, keeping defaults:", err.message);
  }
}

async function restoreConversation() {
  const saved = localStorage.getItem(LS_KEY);
  if (!saved) return;
  try {
    const conv = await getConversation(saved);
    if (!conv) {
      localStorage.removeItem(LS_KEY);
      return;
    }
    conversationId = saved;
    for (const m of conv.messages) {
      if (m.role !== "user" && m.role !== "assistant") continue;
      const content = typeof m.content === "string" ? m.content : "";
      if (!content) continue;
      appendMessage(m.role, content);
      history.push({ role: m.role, content });
    }
  } catch {
    localStorage.removeItem(LS_KEY);
  }
}

async function submit(e) {
  e.preventDefault();
  const text = inputEl.value.trim();
  if (!text) return;
  appendMessage("user", text);
  history.push({ role: "user", content: text });
  inputEl.value = "";
  setSending(true);

  let assistantEl = null;
  let assistantText = "";
  let thinkingEl = null;
  const toolsUsed = [];

  try {
    if (!conversationId) {
      const title = text.length > 60 ? text.slice(0, 60) + "…" : text;
      const conv = await createConversation(title);
      conversationId = conv.id;
      localStorage.setItem(LS_KEY, conversationId);
    }
    await chatStream(
      {
        messages: history,
        model: modelEl.value,
        thinkingBudget: parseInt(effortEl.value, 10),
        conversationId,
      },
      {
        thinking_start: () => {
          thinkingEl = appendMessage("thinking", "🤔 ");
        },
        thinking_delta: ({ text }) => {
          if (thinkingEl) {
            thinkingEl.textContent += text;
            scrollToBottom();
          }
        },
        thinking_stop: () => {
          if (thinkingEl) {
            thinkingEl.classList.add("complete");
            thinkingEl = null;
          }
        },
        tool_use_start: ({ name }) => {
          appendMessage("tool", `🔧 ${name} 호출 중…`);
        },
        tool_use_complete: ({ name }) => {
          toolsUsed.push(name);
          appendMessage("tool", `✓ ${name} 완료`);
        },
        text_delta: ({ text }) => {
          if (!assistantEl) assistantEl = appendMessage("assistant", "");
          assistantText += text;
          assistantEl.textContent = assistantText;
          scrollToBottom();
        },
        message_stop: () => {
          /* end of turn */
        },
        error: ({ message }) => {
          appendMessage("error", `Error: ${message}`);
        },
      },
    );
    if (assistantText) {
      history.push({ role: "assistant", content: assistantText });
    }
    if (onAssistantResponse) onAssistantResponse({ tools_used: toolsUsed });
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
  scrollToBottom();
  return div;
}

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}
