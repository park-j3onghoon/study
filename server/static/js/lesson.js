// Lesson view. iframe src loads /api/lessons/{id}/raw_html — same-origin so the
// lesson's own <form> + fetch can save answers directly.
// Loading indicator: fade in on iframe load event.

let emptyEl = null;
let frameEl = null;

export function init({ emptySelector, frameSelector }) {
  emptyEl = document.querySelector(emptySelector);
  frameEl = document.querySelector(frameSelector);
  frameEl.addEventListener("load", () => {
    frameEl.classList.remove("loading");
  });
}

export function load(conceptId) {
  emptyEl.style.display = "none";
  frameEl.style.display = "block";
  frameEl.classList.add("loading");
  frameEl.src = `/api/lessons/${encodeURIComponent(conceptId)}/raw_html`;
}
