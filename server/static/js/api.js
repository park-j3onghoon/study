// Backend API client. fetch wrappers only — no DOM/state.

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

export function chat({ messages, model, thinkingBudget }) {
  return fetchJson("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      messages,
      model: model || null,
      thinking_budget: thinkingBudget,
    }),
  });
}
