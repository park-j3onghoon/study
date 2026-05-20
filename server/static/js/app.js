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

  // 외부에서 lessons/ 변경 시 사이드바 자동 갱신 (다른 터미널·에디터 등)
  events.subscribe({
    lesson_changed: () => sidebar.refresh(),
    lesson_graded: () => sidebar.refresh(),
    lesson_answered: () => { /* 답이 저장됐다. 사이드바 변화 없음 */ },
  });
}

main().catch((err) => {
  console.error("App init failed:", err);
  alert(`앱 초기화 실패: ${err.message}`);
});
