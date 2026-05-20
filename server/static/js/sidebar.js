// Sidebar: lesson list. Calls back into app when a lesson is selected.
import { listLessons } from "/js/api.js";

let listEl = null;
let onSelect = null;
let activeConceptId = null;

export async function init({ listSelector, onSelect: selectHandler }) {
  listEl = document.querySelector(listSelector);
  onSelect = selectHandler;
  await refresh();
}

export async function refresh() {
  const lessons = await listLessons();
  listEl.innerHTML = "";
  if (lessons.length === 0) {
    const empty = document.createElement("li");
    empty.textContent = "(아직 학습지가 없습니다)";
    empty.style.color = "var(--muted)";
    empty.style.cursor = "default";
    empty.style.fontStyle = "italic";
    listEl.appendChild(empty);
    return;
  }
  for (const lesson of lessons) {
    listEl.appendChild(renderLessonItem(lesson));
  }
}

export function setActive(conceptId) {
  activeConceptId = conceptId;
  for (const li of listEl.children) {
    li.classList.toggle("active", li.dataset.conceptId === conceptId);
  }
}

function renderLessonItem(lesson) {
  const li = document.createElement("li");
  li.dataset.conceptId = lesson.concept_id;

  const title = document.createElement("span");
  title.textContent = lesson.title;
  li.appendChild(title);

  if (lesson.graded) {
    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = "✓ 채점";
    li.appendChild(badge);
  }

  if (lesson.concept_id === activeConceptId) li.classList.add("active");

  li.addEventListener("click", () => {
    setActive(lesson.concept_id);
    onSelect(lesson.concept_id);
  });

  return li;
}
