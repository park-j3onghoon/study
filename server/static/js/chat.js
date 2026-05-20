// SSE-streaming chat. Wires assistant text/thinking/tool events into the DOM live.
import { chatStream } from "/js/api.js";

let messagesEl, formEl, inputEl, modelEl, effortEl, sendBtn;
let onAssistantResponse = null;
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
    await chatStream(
      {
        messages: history,
        model: modelEl.value,
        thinkingBudget: parseInt(effortEl.value, 10),
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
