// TOC sidebar: lists the current lesson's headings, read live from the same-origin
// lesson iframe (/api/lessons/{id}/raw_html), and scrolls the iframe to a heading on
// click. Rebuilds on each lesson load. Works for every lesson with no regeneration.
let frameEl = null;
let listEl = null;

export function init({ frameSelector, listSelector }) {
  frameEl = document.querySelector(frameSelector);
  listEl = document.querySelector(listSelector);
  if (!frameEl || !listEl) return;
  frameEl.addEventListener("load", build);
  build();
}

function build() {
  listEl.innerHTML = "";
  const headings = readHeadings();
  if (!headings.length) {
    const li = document.createElement("li");
    li.className = "toc-empty";
    li.textContent = "(목차 없음)";
    listEl.appendChild(li);
    return;
  }
  const top = headings[0].level; // normalize indent to the shallowest heading present
  for (const h of headings) {
    const li = document.createElement("li");
    li.className = "toc-item";
    li.textContent = h.text;
    li.title = h.text;
    li.style.setProperty("--toc-depth", String(Math.min(Math.max(h.level - top, 0), 3)));
    li.addEventListener("click", () => h.el.scrollIntoView({ behavior: "smooth", block: "start" }));
    listEl.appendChild(li);
  }
}

function readHeadings() {
  let doc;
  try {
    doc = frameEl.contentDocument; // same-origin iframe → readable
  } catch {
    return [];
  }
  if (!doc) return [];
  const out = [];
  for (const el of doc.querySelectorAll("h1, h2, h3, h4")) {
    const text = (el.textContent || "").trim();
    if (text) out.push({ el, level: Number(el.tagName[1]), text });
  }
  return out;
}
