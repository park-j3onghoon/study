// Backend API client. fetch wrappers + SSE chat stream.

async function fetchJson(url, options = {}) {
  const r = await fetch(url, options);
  if (!r.ok) {
    const body = await r.text().catch(() => "");
    throw new Error(`${options.method || "GET"} ${url} → ${r.status}: ${body}`);
  }
  return r.json();
}

export function listLessons() {
  return fetchJson("/api/lessons");
}

export function getLesson(conceptId) {
  return fetchJson(`/api/lessons/${encodeURIComponent(conceptId)}`);
}

export function saveAnswers(conceptId, answers) {
  return fetchJson(`/api/lessons/${encodeURIComponent(conceptId)}/answers`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answers }),
  });
}

export async function getResult(conceptId) {
  const r = await fetch(`/api/lessons/${encodeURIComponent(conceptId)}/result`);
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(`getResult ${r.status}`);
  return r.json();
}

export function listConversations() {
  return fetchJson("/api/conversations");
}

export function createConversation(title) {
  return fetchJson("/api/conversations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
}

export async function getConversation(id) {
  const r = await fetch(`/api/conversations/${encodeURIComponent(id)}`);
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(`getConversation ${r.status}`);
  return r.json();
}

// SSE chat stream.
// callbacks: { thinking_start, thinking_delta, thinking_stop, text_delta,
//              tool_use_start, tool_use_complete, message_stop, error, unknown }
export async function chatStream({ messages, model, thinkingBudget, conversationId }, callbacks) {
  const resp = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json", "Accept": "text/event-stream" },
    body: JSON.stringify({
      messages,
      model: model || null,
      thinking_budget: thinkingBudget,
      conversation_id: conversationId || null,
    }),
  });
  if (!resp.ok) {
    const body = await resp.text().catch(() => "");
    throw new Error(`chat ${resp.status}: ${body}`);
  }
  for await (const { event, data } of readSSE(resp)) {
    const handler = callbacks[event];
    if (handler) handler(data || {});
    else if (callbacks.unknown) callbacks.unknown(event, data);
  }
}

async function* readSSE(response) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      const tail = buffer.trim();
      if (tail) {
        const ev = parseSSEEvent(tail);
        if (ev) yield ev;
      }
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    let idx;
    while ((idx = buffer.indexOf("\n\n")) >= 0) {
      const chunk = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      const ev = parseSSEEvent(chunk);
      if (ev) yield ev;
    }
  }
}

function parseSSEEvent(chunk) {
  let event = "message";
  const dataLines = [];
  for (const line of chunk.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
  }
  if (dataLines.length === 0) return null;
  try {
    return { event, data: JSON.parse(dataLines.join("")) };
  } catch {
    return null;
  }
}
