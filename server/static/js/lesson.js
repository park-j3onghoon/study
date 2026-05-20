// Lesson view. Displays a lesson HTML in a sandboxed iframe and listens for
// postMessage from inside the iframe to forward answers to the backend.
import { getLesson, saveAnswers } from "/js/api.js";

let emptyEl = null;
let frameEl = null;
let currentConceptId = null;

export function init({ emptySelector, frameSelector }) {
  emptyEl = document.querySelector(emptySelector);
  frameEl = document.querySelector(frameSelector);

  // 한 번만 등록. 메시지의 concept_id로 현재 학습지인지 확인.
  window.addEventListener("message", handlePostMessage);
}

export async function load(conceptId) {
  const { lesson_html } = await getLesson(conceptId);
  currentConceptId = conceptId;
  emptyEl.style.display = "none";
  frameEl.style.display = "block";
  // srcdoc 으로 띄우면 origin 이 null 이라 같은 origin 의 fetch 가 막힌다.
  // 답안은 postMessage 로만 부모에게 전달하도록 한다.
  frameEl.srcdoc = lesson_html;
}

async function handlePostMessage(event) {
  const data = event.data;
  if (!data || data.type !== "save_answers") return;
  if (!data.concept_id || data.concept_id !== currentConceptId) return;
  try {
    await saveAnswers(data.concept_id, data.answers || {});
    // iframe 안에 ack 보내기. 학습지가 그걸 받아 UI 갱신.
    frameEl.contentWindow?.postMessage({ type: "answers_saved" }, "*");
  } catch (err) {
    frameEl.contentWindow?.postMessage(
      { type: "answers_save_error", message: String(err.message || err) },
      "*",
    );
  }
}
