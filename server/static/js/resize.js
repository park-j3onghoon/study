// Drag handles that resize panels: chat height, left lesson-list width, right TOC width.
// Each size lives in a CSS var (a grid track) and persists in localStorage, re-clamped to
// the viewport on restore. Width/height vars are independent of the hide toggles' *-shown
// multipliers, so dragging and collapsing never fight over the same value.
const MIN_PX = 80;          // a panel can't shrink below this
const CENTER_MIN_PX = 150;  // always leave this for the lesson (the flexible track)

const PANELS = [
  { sel: "#chat-resizer", cssVar: "--chat-h", lsKey: "study.chat_h", cursor: "row-resize",
    sizeFrom: (e) => window.innerHeight - e.clientY, avail: () => window.innerHeight },
  { sel: "#lessons-resizer", cssVar: "--lessons-w", lsKey: "study.lessons_w", cursor: "col-resize",
    sizeFrom: (e) => e.clientX, avail: () => window.innerWidth },
  { sel: "#toc-resizer", cssVar: "--toc-w", lsKey: "study.toc_w", cursor: "col-resize",
    sizeFrom: (e) => window.innerWidth - e.clientX, avail: () => window.innerWidth },
];

export function init() {
  for (const p of PANELS) {
    const el = document.querySelector(p.sel);
    if (!el) continue;
    restore(p);
    el.addEventListener("pointerdown", (e) => onDown(e, p));
  }
}

function onDown(e, p) {
  e.preventDefault();
  const move = (ev) => setSize(p, p.sizeFrom(ev));
  const up = () => {
    window.removeEventListener("pointermove", move);
    document.body.classList.remove("resizing");
    document.body.style.cursor = "";
    persist(p);
  };
  window.addEventListener("pointermove", move);
  window.addEventListener("pointerup", up, { once: true });
  document.body.classList.add("resizing");
  document.body.style.cursor = p.cursor;
}

function setSize(p, px) {
  const max = p.avail() - CENTER_MIN_PX;
  const v = Math.max(MIN_PX, Math.min(px, max));
  document.body.style.setProperty(p.cssVar, `${v}px`);
}

function persist(p) {
  const v = document.body.style.getPropertyValue(p.cssVar);
  try { if (v) localStorage.setItem(p.lsKey, v); } catch { /* private mode: ignore */ }
}

function restore(p) {
  let saved;
  try { saved = localStorage.getItem(p.lsKey); } catch { return; }
  if (saved) setSize(p, parseInt(saved, 10));
}
