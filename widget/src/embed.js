/**
 * Embeddable chat widget. Single <script> tag on the customer's site:
 *
 *   <script src=".../embed.js"
 *           data-bot-api="https://backend/api"
 *           data-position="right"
 *           data-accent="#e87722"
 *           data-title="Support"
 *           data-greeting="Hallo! Wie kann ich helfen?" defer></script>
 *
 * Renders a launcher tab on the chosen side; click slides a chat panel out.
 * Everything lives in a Shadow DOM so the host page's CSS can't leak in.
 */
(function () {
  const script = document.currentScript;
  const cfg = {
    api: script.getAttribute("data-bot-api") || "http://localhost:8000/api",
    position: script.getAttribute("data-position") || "right",
    accent: script.getAttribute("data-accent") || "#e87722",
    title: script.getAttribute("data-title") || "Support",
    greeting:
      script.getAttribute("data-greeting") || "Hallo! Wie kann ich helfen?",
  };

  const sessionId =
    localStorage.getItem("chatbot_session") ||
    (() => {
      const id = "s_" + Math.random().toString(36).slice(2) + Date.now();
      localStorage.setItem("chatbot_session", id);
      return id;
    })();

  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = host.attachShadow({ mode: "open" });

  root.innerHTML = `
    <style>
      :host { all: initial; }
      * { box-sizing: border-box; font-family: system-ui, sans-serif; }
      .launcher {
        position: fixed; bottom: 24px; ${cfg.position}: 24px;
        width: 56px; height: 56px; border-radius: 50%; border: none;
        background: ${cfg.accent}; color: #fff; font-size: 24px; cursor: pointer;
        box-shadow: 0 4px 16px rgba(0,0,0,.25); z-index: 2147483646;
      }
      .panel {
        position: fixed; bottom: 0; ${cfg.position}: 0; top: 0;
        width: 380px; max-width: 100vw; background: #fff;
        display: flex; flex-direction: column;
        box-shadow: -4px 0 24px rgba(0,0,0,.2);
        transform: translateX(${cfg.position === "right" ? "100%" : "-100%"});
        transition: transform .25s ease; z-index: 2147483647;
      }
      .panel.open { transform: translateX(0); }
      .head {
        background: ${cfg.accent}; color: #fff; padding: 16px;
        display: flex; justify-content: space-between; align-items: center;
      }
      .head h3 { margin: 0; font-size: 16px; }
      .head button { background: none; border: none; color: #fff; font-size: 20px; cursor: pointer; }
      .msgs { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 10px; }
      .msg { max-width: 80%; padding: 8px 12px; border-radius: 12px; line-height: 1.4; white-space: pre-wrap; }
      .msg.user { align-self: flex-end; background: ${cfg.accent}; color: #fff; }
      .msg.bot { align-self: flex-start; background: #f0f0f0; color: #111; }
      .foot { display: flex; gap: 8px; padding: 12px; border-top: 1px solid #eee; }
      .foot input { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 8px; }
      .foot button { background: ${cfg.accent}; color: #fff; border: none; border-radius: 8px; padding: 0 16px; cursor: pointer; }
    </style>
    <button class="launcher" aria-label="Chat oeffnen">&#128172;</button>
    <div class="panel" role="dialog" aria-label="${cfg.title}">
      <div class="head"><h3>${cfg.title}</h3><button class="close" aria-label="Schliessen">&times;</button></div>
      <div class="msgs"></div>
      <form class="foot">
        <input type="text" placeholder="Nachricht..." autocomplete="off" />
        <button type="submit">Senden</button>
      </form>
    </div>
  `;

  const panel = root.querySelector(".panel");
  const msgs = root.querySelector(".msgs");
  const form = root.querySelector(".foot");
  const input = root.querySelector("input");

  function addMsg(text, who) {
    const el = document.createElement("div");
    el.className = "msg " + who;
    el.textContent = text;
    msgs.appendChild(el);
    msgs.scrollTop = msgs.scrollHeight;
    return el;
  }

  root.querySelector(".launcher").onclick = () => {
    panel.classList.add("open");
    if (!msgs.childElementCount) addMsg(cfg.greeting, "bot");
    input.focus();
  };
  root.querySelector(".close").onclick = () => panel.classList.remove("open");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    addMsg(text, "user");
    const botEl = addMsg("", "bot");

    try {
      const res = await fetch(cfg.api + "/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message: text }),
      });
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const parts = buf.split("\n\n");
        buf = parts.pop();
        for (const part of parts) {
          const line = part.replace(/^data: /, "");
          if (!line) continue;
          const evt = JSON.parse(line);
          if (evt.type === "token") {
            botEl.textContent += evt.content;
            msgs.scrollTop = msgs.scrollHeight;
          } else if (evt.type === "error") {
            botEl.textContent += "\n[Fehler: " + evt.message + "]";
          }
        }
      }
    } catch (err) {
      botEl.textContent = "Verbindungsfehler. Bitte spaeter erneut versuchen.";
    }
  });
})();
