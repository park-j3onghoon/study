// Completion cue: when a generated lesson becomes ready while the tab is in the
// background, flash the document title so a user who switched away notices. The
// title is restored when the tab is shown again.
//
// Note: browsers block JS from stealing OS window focus (anti-focus-stealing), so
// we can't pull the window forward on our own. A clickable desktop Notification is
// the only legitimate "refocus" path — deferred to an opt-in follow-up (2d-2).
const READY_TITLE = "✅ 학습지 준비됨";

let baseTitle = null;
let flashing = false;

export function init() {
  baseTitle = document.title;
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) restore();
  });
}

// Call when a lesson finished generating. Only flashes if the tab is hidden —
// if the user is already looking, there's nothing to alert.
export function signalReady() {
  if (!document.hidden) return;
  flashing = true;
  document.title = READY_TITLE;
}

function restore() {
  if (!flashing) return;
  flashing = false;
  document.title = baseTitle;
}
