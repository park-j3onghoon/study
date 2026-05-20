// App entry point. Wires sidebar, lesson view, and chat together.
import * as sidebar from "/js/sidebar.js";
import * as lesson from "/js/lesson.js";
import * as chat from "/js/chat.js";

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
      // 새 학습지가 만들어졌거나 결과가 저장됐을 가능성 → 사이드바 새로고침
      const tools = resp.tools_used || [];
      if (tools.includes("write_lesson") || tools.includes("grade_lesson")) {
        await sidebar.refresh();
      }
    },
  });
}

main().catch((err) => {
  console.error("App init failed:", err);
  alert(`앱 초기화 실패: ${err.message}`);
});
