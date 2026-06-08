// Drag the gutter between the lesson area and the chat panel to resize chat height.
// Height lives in the --chat-h CSS var (grid track) and persists in localStorage;
// it is re-clamped to the viewport on restore so a tall saved value can't bury the lesson.
const LS_KEY = "study.chat_h";
const MIN_PX = 80;
const LESSON_MIN_PX = 150; // 채팅이 아무리 커도 학습지에 남길 최소 높이

let resizerEl = null;

export function init({ resizerSelector }) {
  resizerEl = document.querySelector(resizerSelector);
  if (!resizerEl) return;
  restore();
  resizerEl.addEventListener("pointerdown", onPointerDown);
}

function onPointerDown(e) {
  e.preventDefault(); // 텍스트 선택 시작 방지
  window.addEventListener("pointermove", onPointerMove);
  window.addEventListener("pointerup", onPointerUp, { once: true });
  document.body.classList.add("resizing");
}

function onPointerMove(e) {
  setHeight(window.innerHeight - e.clientY);
}

function onPointerUp() {
  window.removeEventListener("pointermove", onPointerMove);
  document.body.classList.remove("resizing");
  persist();
}

function setHeight(px) {
  const max = window.innerHeight - LESSON_MIN_PX;
  const h = Math.max(MIN_PX, Math.min(px, max));
  document.body.style.setProperty("--chat-h", `${h}px`);
}

function persist() {
  const v = document.body.style.getPropertyValue("--chat-h");
  try { if (v) localStorage.setItem(LS_KEY, v); } catch { /* private mode: ignore */ }
}

function restore() {
  let saved;
  try { saved = localStorage.getItem(LS_KEY); } catch { return; }
  if (!saved) return;
  setHeight(parseInt(saved, 10));
}
