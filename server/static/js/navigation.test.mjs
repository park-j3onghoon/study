// Unit test for navigation.intendedConceptId — the postMessage trust boundary.
// Frameless: runs under plain `node` (no DOM, no test framework). Driven from pytest
// via tests/test_navigation.py. Table-driven, mirroring tests/test_tools.py's _args(**overrides):
// start from a valid message and corrupt one field per case.
//
// The import below is the FIRST assertion: if navigation.js stops being import-safe
// (touches `window` at module top level), this line throws and the whole test goes red —
// which keeps intendedConceptId honestly DOM-free.
import assert from "node:assert/strict";
import { intendedConceptId } from "./navigation.js";

const APP_ORIGIN = "https://app.example";
const FRAME = { name: "lesson-frame" };      // stand-in for the iframe's contentWindow
const OTHER = { name: "some-other-window" };  // a different same-origin frame/popup
const isTrustedSource = (src) => src === FRAME;

// A message that passes every check.
const valid = () => ({
  origin: APP_ORIGIN,
  source: FRAME,
  data: { type: "navigate_lesson", concept_id: "argo-cd" },
});

const call = (msg) => intendedConceptId(msg, { appOrigin: APP_ORIGIN, isTrustedSource });

// [label, message, expected]
const cases = [
  ["valid → concept_id", valid(), "argo-cd"],
  ["origin mismatch", { ...valid(), origin: "https://evil.example" }, null],
  ["source untrusted (other frame)", { ...valid(), source: OTHER }, null],
  ["origin ok but source wrong (combo)", { ...valid(), origin: APP_ORIGIN, source: OTHER }, null],
  ["source undefined", { ...valid(), source: undefined }, null],
  ["data null", { ...valid(), data: null }, null],
  ["data string (non-object)", { ...valid(), data: "navigate_lesson" }, null],
  ["data number (non-object)", { ...valid(), data: 42 }, null],
  ["data array (non-object-shape)", { ...valid(), data: ["navigate_lesson"] }, null],
  ["data function (non-object)", { ...valid(), data: () => {} }, null],
  ["wrong type", { ...valid(), data: { type: "something_else", concept_id: "argo-cd" } }, null],
  ["concept_id key missing", { ...valid(), data: { type: "navigate_lesson" } }, null],
  ["concept_id number (non-string)", { ...valid(), data: { type: "navigate_lesson", concept_id: 42 } }, null],
  ["concept_id object (non-string)", { ...valid(), data: { type: "navigate_lesson", concept_id: {} } }, null],
  ["concept_id null (non-string)", { ...valid(), data: { type: "navigate_lesson", concept_id: null } }, null],
  // boolean is the trap: if the guard ever narrows to `== null`, String(true) → "true" would
  // coerce-pass the lowercase slug regex. The typeof check must reject it.
  ["concept_id boolean true (truthy non-string)", { ...valid(), data: { type: "navigate_lesson", concept_id: true } }, null],
  ["concept_id empty string", { ...valid(), data: { type: "navigate_lesson", concept_id: "" } }, null],
  ["bad slug: path traversal", { ...valid(), data: { type: "navigate_lesson", concept_id: "../secret" } }, null],
  ["bad slug: uppercase", { ...valid(), data: { type: "navigate_lesson", concept_id: "ArgoCD" } }, null],
  ["bad slug: space", { ...valid(), data: { type: "navigate_lesson", concept_id: "argo cd" } }, null],
  ["bad slug: leading hyphen", { ...valid(), data: { type: "navigate_lesson", concept_id: "-argo" } }, null],
  ["message null (defensive)", null, null],
];

let failures = 0;
for (const [label, msg, expected] of cases) {
  try {
    const got = call(msg);
    assert.equal(got, expected, `${label}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(got)}`);
    console.log(`  ok  ${label}`);
  } catch (err) {
    failures += 1;
    console.error(`FAIL  ${label} — ${err.message}`);
  }
}

if (failures > 0) {
  console.error(`\n${failures} case(s) failed`);
  process.exit(1);
}
console.log(`\nall ${cases.length} cases passed`);
