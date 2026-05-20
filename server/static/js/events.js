// Server-Sent Events client for /api/events.
// Subscribers register per-event handlers; this module reconnects on error.

export function subscribe(handlers) {
  const source = new EventSource("/api/events");
  for (const [name, handler] of Object.entries(handlers)) {
    source.addEventListener(name, (e) => {
      let data = {};
      try { data = e.data ? JSON.parse(e.data) : {}; } catch {}
      handler(data);
    });
  }
  source.onerror = () => {
    // 브라우저가 EventSource는 자동 재연결하지만 명시적 로그
    console.warn("/api/events disconnected, browser will retry");
  };
  return source;
}
