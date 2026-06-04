// Sidebar: lesson tree. Lessons form a parent_id adjacency list (flat on the
// wire); this rebuilds the tree by grouping children under their parent.
// Calls back into app when a lesson is selected.
import { listLessons } from "/js/api.js";

const MAX_DEPTH = 20; // secondary cycle guard (visited-set is primary)

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
    listEl.appendChild(renderEmpty());
    return;
  }
  const { roots, childrenByParent } = buildTree(lessons);
  for (const root of roots) {
    listEl.appendChild(renderTreeItem(root, 0, new Set(), childrenByParent));
  }
}

// Active highlight walks the whole nested tree, not just top-level rows.
export function setActive(conceptId) {
  activeConceptId = conceptId;
  for (const row of listEl.querySelectorAll("[data-concept-id]")) {
    row.classList.toggle("active", row.dataset.conceptId === conceptId);
  }
}

// Pure: flat lessons → {roots, childrenByParent}. A lesson is a root when its
// parent_id is null/absent OR points to an id not in the list (dangling parent
// from external git edits → fall back to root so nothing disappears). Lessons
// trapped in a pure cycle (a↔b, possible after a git merge) reach no root via
// children, so they'd vanish; promote any unreached node to a root too.
export function buildTree(lessons) {
  const byId = new Map(lessons.map((l) => [l.concept_id, l]));
  const childrenByParent = new Map();
  const roots = [];
  for (const lesson of lessons) {
    const parentId = lesson.parent_id;
    if (parentId != null && byId.has(parentId)) {
      if (!childrenByParent.has(parentId)) childrenByParent.set(parentId, []);
      childrenByParent.get(parentId).push(lesson);
    } else {
      roots.push(lesson);
    }
  }
  for (const lesson of lessons) {
    if (!reachableFromRoots(lesson, roots, childrenByParent)) roots.push(lesson);
  }
  return { roots, childrenByParent };
}

// True if `lesson` already renders under some root (walks children with a
// visited-set so a cycle terminates). Used to rescue cycle-trapped orphans.
function reachableFromRoots(lesson, roots, childrenByParent) {
  const target = lesson.concept_id;
  const stack = [...roots];
  const seen = new Set();
  while (stack.length) {
    const node = stack.pop();
    if (node.concept_id === target) return true;
    if (seen.has(node.concept_id)) continue;
    seen.add(node.concept_id);
    stack.push(...(childrenByParent.get(node.concept_id) || []));
  }
  return false;
}

// Recursive. visited-set + MAX_DEPTH keep a cycle (a parent_id chain that loops,
// possible when a git merge bypasses write-time validation) from recursing
// forever. A visited node is rendered as a leaf to break the loop.
function renderTreeItem(lesson, depth, visited, childrenByParent) {
  const conceptId = lesson.concept_id;
  const children =
    visited.has(conceptId) || depth >= MAX_DEPTH
      ? []
      : childrenByParent.get(conceptId) || [];

  const li = document.createElement("li");
  li.className = "tree-node";

  const row = renderRow(lesson, depth, children.length > 0);
  li.appendChild(row);

  if (children.length > 0) {
    const nested = document.createElement("ul");
    nested.className = "tree-children";
    const nextVisited = new Set(visited).add(conceptId);
    for (const child of children) {
      nested.appendChild(renderTreeItem(child, depth + 1, nextVisited, childrenByParent));
    }
    li.appendChild(nested);
    wireCaret(li, row.querySelector(".caret"));
  }

  return li;
}

function renderRow(lesson, depth, hasChildren) {
  const row = document.createElement("div");
  row.className = "tree-row";
  row.dataset.conceptId = lesson.concept_id;
  row.style.setProperty("--depth", String(depth));

  const caret = document.createElement("span");
  caret.className = "caret";
  if (!hasChildren) caret.classList.add("leaf");
  row.appendChild(caret);

  const title = document.createElement("span");
  title.className = "tree-title";
  title.textContent = lesson.title;
  row.appendChild(title);

  if (lesson.graded) {
    const badge = document.createElement("span");
    badge.className = "badge";
    badge.textContent = "✓ 채점";
    row.appendChild(badge);
  }

  if (lesson.concept_id === activeConceptId) row.classList.add("active");

  row.addEventListener("click", () => {
    setActive(lesson.concept_id);
    onSelect(lesson.concept_id);
  });

  return row;
}

// Caret toggles the collapsed class on the li without selecting the lesson.
function wireCaret(li, caret) {
  caret.addEventListener("click", (e) => {
    e.stopPropagation();
    li.classList.toggle("collapsed");
  });
}

function renderEmpty() {
  const empty = document.createElement("li");
  empty.className = "tree-empty";
  empty.textContent = "(아직 학습지가 없습니다)";
  return empty;
}
