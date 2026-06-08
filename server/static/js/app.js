// App entry point. Wires sidebar, lesson view, chat, and server-push events together.
import * as sidebar from "/js/sidebar.js";
import * as lesson from "/js/lesson.js";
import * as chat from "/js/chat.js";
import * as events from "/js/events.js";
import * as focus from "/js/focus.js";
import * as notify from "/js/notify.js";
import * as navigation from "/js/navigation.js";
import * as resize from "/js/resize.js";

// The one "show this lesson in the center" action: highlight it in the sidebar tree and
// load it into the iframe. Shared by every external trigger — chat focus 응답, 그리고
// 지도(부모)→자식 postMessage 네비게이션. (사이드바 클릭은 renderRow가 setActive 후
// onSelect→lesson.load 로 같은 결과를 낸다.)
const showLesson = (conceptId) => {
  sidebar.setActive(conceptId);
  lesson.load(conceptId);
};

const DISTILL_PROMPT =
  "오늘 학습 정리: 오늘 Claude 세션에서 새로 배운 것과 끈질긴 논의 끝의 결론을 일반 " +
  "소프트웨어 엔지니어링 학습 내용으로 추려 주제별 학습지로 만들고, 학습지 트리도 정리해줘. " +
  "회사 고유 정보(내부 시스템/서비스 이름 등)는 빼고 일반화해줘.";

async function main() {
  lesson.init({
    emptySelector: "#lesson-empty",
    frameSelector: "#lesson-frame",
  });

  await sidebar.init({
    listSelector: "#lesson-list",
    onSelect: (conceptId) => lesson.load(conceptId),
  });

  chat.init({
    messagesSelector: "#chat-messages",
    formSelector: "#chat-form",
    inputSelector: "#chat-input",
    modelSelector: "#model-select",
    onAssistantResponse: async (resp) => {
      // 채팅 응답 직후에도 갱신 (이벤트 늦으면 fallback)
      const tools = resp.tools_used || [];
      if (tools.includes("write_lesson") || tools.includes("grade_lesson")) {
        await sidebar.refresh();
      }
      // 자동 표시는 이제 이 경로로만: agent가 focus=true로 쓴 학습지를 한 번 로드.
      // (파일 이벤트는 사이드바 refresh 전용으로 decouple됨.)
      if (resp.focus_concept_id) {
        showLesson(resp.focus_concept_id);
      }
      // focus 모드에선 메시지가 숨겨져 있으니 새 응답을 unread 점으로 알린다.
      focus.markUnread();
    },
  });

  const distillBtn = document.querySelector("#distill-today");
  if (distillBtn) distillBtn.addEventListener("click", () => chat.sendMessage(DISTILL_PROMPT));

  focus.init({ toggleSelector: "#focus-toggle" });
  resize.init({ resizerSelector: "#chat-resizer" });
  notify.init();

  // 지도(부모) 학습지가 iframe 안에서 postMessage 로 보낸 자식 네비게이션을 받는다.
  // isTrustedSource=lesson.isLessonFrame 로 그 lesson iframe 의 메시지만 신뢰한다.
  navigation.init({ onNavigate: showLesson, isTrustedSource: lesson.isLessonFrame });

  // lessons/ 변경 시: 사이드바 refresh 전용. 자동 iframe 로드는 더 이상 여기서 안 함
  // (클러스터 재작성 시 형제 학습지 변경이 가운데 iframe을 가로채는 yank/깜빡임 방지).
  // 클러스터 재작성은 짧은 시간에 N개 lesson_changed를 쏟아내므로 ~300ms 디바운스로
  // refresh를 1회로 coalesce한다.
  events.subscribe({
    lesson_changed: () => {
      refreshSidebarDebounced();
      notify.signalReady(); // 탭이 백그라운드면 제목 깜빡여 생성 완료 알림
    },
    lesson_graded: () => sidebar.refresh(),
    lesson_answered: () => { /* 답이 저장됐다. 사이드바 변화 없음 */ },
  });
}

const REFRESH_DEBOUNCE_MS = 300;
let refreshTimer = null;

// 연속된 lesson_changed(클러스터 재작성 등)를 모아 사이드바 refresh를 1회로 합친다.
function refreshSidebarDebounced() {
  if (refreshTimer) clearTimeout(refreshTimer);
  refreshTimer = setTimeout(() => {
    refreshTimer = null;
    sidebar.refresh();
  }, REFRESH_DEBOUNCE_MS);
}

main().catch((err) => {
  console.error("App init failed:", err);
  alert(`앱 초기화 실패: ${err.message}`);
});
