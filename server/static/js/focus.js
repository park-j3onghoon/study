// Focus mode: hide the sidebar + the whole chat panel so the lesson fills the screen.
// Toggle with the 📖 button or `f`; exit with `Esc`. State persists in localStorage.
// Keyboard shortcuts are suppressed while an editable field has focus, so typing
// "f" in the chat box doesn't toggle. New chat content arriving while focused
// (the message stream is hidden then) raises an unread dot on the toggle.
const LS_KEY = "study.focus";
const FOCUS_CLASS = "focus";
const UNREAD_CLASS = "has-unread";

let toggleEl = null;

export function init({ toggleSelector }) {
  toggleEl = document.querySelector(toggleSelector);
  if (readPersisted()) apply(true);

  toggleEl.addEventListener("click", toggle);
  document.addEventListener("keydown", onKeydown);
}

// Called by app.js when an assistant turn completes. Only signals while focused —
// that's when the chat message stream is hidden and could be missed.
export function markUnread() {
  if (document.body.classList.contains(FOCUS_CLASS)) {
    toggleEl.classList.add(UNREAD_CLASS);
  }
}

function toggle() {
  apply(!document.body.classList.contains(FOCUS_CLASS));
}

function apply(on) {
  document.body.classList.toggle(FOCUS_CLASS, on);
  toggleEl.setAttribute("aria-pressed", String(on));
  if (!on) toggleEl.classList.remove(UNREAD_CLASS); // exiting → reading messages now
  persist(on);
}

function onKeydown(e) {
  if (isEditable(document.activeElement)) return; // don't hijack typing
  if (e.key === "f" || e.key === "F") {
    e.preventDefault();
    toggle();
  } else if (e.key === "Escape" && document.body.classList.contains(FOCUS_CLASS)) {
    apply(false);
  }
}

function isEditable(el) {
  if (!el) return false;
  const tag = el.tagName;
  return tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || el.isContentEditable;
}

function persist(on) {
  try { localStorage.setItem(LS_KEY, on ? "1" : "0"); } catch { /* private mode: ignore */ }
}

function readPersisted() {
  try { return localStorage.getItem(LS_KEY) === "1"; } catch { return false; }
}
