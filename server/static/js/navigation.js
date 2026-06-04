// Cross-frame navigation: a "map" (parent) lesson, rendered inside the same-origin
// lesson iframe, asks the app to open one of its child lessons by posting
//   { type: "navigate_lesson", concept_id } → window.parent.
//
// SENDER side lives in app/infrastructure/config.py system_prompt 【규칙 1.6】 — the LLM
// emits the postMessage snippet into lesson_html. The message type/fields here and the
// snippet there are an UNSYNCHRONIZED contract (one is a JS constant, the other is prose
// the model reproduces). If you rename NAVIGATE_TYPE or the fields, update that prompt
// block too, or the map buttons go silently dead.
//
// SECURITY (Sec#11): act only on a message that is (1) from our own origin,
// (2) sourced from the lesson iframe's window, (3) shaped exactly as our protocol,
// (4) a concept_id matching the slug regex. Everything else is ignored silently —
// postMessage is an open channel. NOTE: these checks guard against foreign-origin
// embeds, other frames/popups, and noise; they do NOT isolate a malicious lesson_html
// (the iframe has allow-same-origin + allow-scripts and could escape its sandbox).
// Trusting the lesson body itself is a separate concern, out of scope here.
const NAVIGATE_TYPE = "navigate_lesson";
// MUST mirror app/domain/models.py _CONCEPT_ID_RE (JS can't import it); drift = silent 404.
const CONCEPT_ID_RE = /^[a-z0-9][a-z0-9-]*$/;

// Pure + DOM-free so it can be unit-tested under node. Returns the concept_id to open,
// or null if the message fails any check. Every access is type-guarded, so it never throws
// on the inputs that can actually reach it: real MessageEvent.data is produced by the
// structured-clone algorithm — a plain value graph with no accessors/Proxies — so a hostile
// lesson_html can't deliver a throwing getter. (A hand-built object with a throwing `type`
// getter would propagate; that path doesn't exist over postMessage.)
export function intendedConceptId(message, { appOrigin, isTrustedSource }) {
  if (!message || message.origin !== appOrigin) return null;
  if (!isTrustedSource(message.source)) return null;
  const data = message.data;
  if (typeof data !== "object" || data === null) return null;
  if (data.type !== NAVIGATE_TYPE) return null;
  const conceptId = data.concept_id;
  if (typeof conceptId !== "string" || !CONCEPT_ID_RE.test(conceptId)) return null;
  return conceptId;
}

// Module-level handle so init() is idempotent — a second call replaces the listener
// instead of stacking a duplicate (a window 'message' listener is append-only, unlike
// the element listeners the sibling modules bind).
let handler = null;

export function init({ onNavigate, isTrustedSource }) {
  if (handler) window.removeEventListener("message", handler);
  handler = (event) => {
    const conceptId = intendedConceptId(event, { appOrigin: location.origin, isTrustedSource });
    if (conceptId !== null) onNavigate(conceptId);
  };
  window.addEventListener("message", handler);
}
