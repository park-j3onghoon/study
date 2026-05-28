// App entry point. Wires sidebar, lesson view, chat, and server-push events together.
import * as sidebar from "/js/sidebar.js";
import * as lesson from "/js/lesson.js";
import * as chat from "/js/chat.js";
import * as events from "/js/events.js";

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
    effortSelector: "#effort-select",
    onAssistantResponse: async (resp) => {
      // 채팅 응답 직후에도 갱신 (이벤트 늦으면 fallback)
      const tools = resp.tools_used || [];
      if (tools.includes("write_lesson") || tools.includes("grade_lesson")) {
        await sidebar.refresh();
      }
    },
  });

  // lessons/ 변경 시: 사이드바 갱신 + 새 학습지면 가운데 iframe에 자동 로드.
  // write_lesson tool이 완료되자마자 사용자가 클릭 없이 학습 시작할 수 있게.
  events.subscribe({
    lesson_changed: async ({ concept_id }) => {
      await sidebar.refresh();
      if (concept_id) {
        sidebar.setActive(concept_id);
        lesson.load(concept_id);
      }
    },
    lesson_graded: () => sidebar.refresh(),
    lesson_answered: () => { /* 답이 저장됐다. 사이드바 변화 없음 */ },
  });
}

main().catch((err) => {
  console.error("App init failed:", err);
  alert(`앱 초기화 실패: ${err.message}`);
});
