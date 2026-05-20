// Lesson view. iframe src loads /api/lessons/{id}/raw_html — same-origin so the
// lesson's own <form> + fetch can save answers directly. No postMessage bridge needed.

let emptyEl = null;
let frameEl = null;

export function init({ emptySelector, frameSelector }) {
  emptyEl = document.querySelector(emptySelector);
  frameEl = document.querySelector(frameSelector);
}

export function load(conceptId) {
  emptyEl.style.display = "none";
  frameEl.style.display = "block";
  frameEl.src = `/api/lessons/${encodeURIComponent(conceptId)}/raw_html`;
}
