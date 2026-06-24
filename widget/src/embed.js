/**
 * Embeddable chat widget. Single <script> tag on the customer's site:
 *
 *   <script src=".../embed.js"
 *           data-bot-api="https://backend/api"
 *           data-position="right"
 *           data-accent="#e87722"
 *           data-title="Support"
 *           data-greeting="Hallo! Wie kann ich helfen?"
 *           data-logo="https://cdn.example.com/logo.svg" defer></script>
 *
 * Renders a launcher tab on the chosen side; click slides a chat panel out.
 * Everything lives in a Shadow DOM so the host page's CSS can't leak in.
 *
 * Styling contract -- set these CSS custom properties on the host page
 * (on #chatbot-widget or :root) to restyle without touching this file. The
 * font file itself must be loaded by the host page; here we only reference it.
 *
 *   #chatbot-widget {
 *     --chatbot-font: "Inter", system-ui, sans-serif;
 *     --chatbot-accent: #e87722;        --chatbot-on-accent: #fff;
 *     --chatbot-bg: #fff;               --chatbot-text: #111;
 *     --chatbot-bot-bg: #f0f0f0;        --chatbot-bot-text: #111;
 *     --chatbot-radius: 12px;           --chatbot-input-radius: 8px;
 *     --chatbot-width: 380px;           --chatbot-launcher-size: 56px;
 *     --chatbot-logo-height: 24px;      --chatbot-title-size: 16px;
 *   }
 *
 * data-accent is the fallback for --chatbot-accent; CSS variables win when set.
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
    logo: script.getAttribute("data-logo") || "",
  };

  const sessionId =
    localStorage.getItem("chatbot_session") ||
    (() => {
      const id = "s_" + Math.random().toString(36).slice(2) + Date.now();
      localStorage.setItem("chatbot_session", id);
      return id;
    })();

  const host = document.createElement("div");
  host.id = "chatbot-widget";
  document.body.appendChild(host);
  const root = host.attachShadow({ mode: "open" });

  root.innerHTML = `
    <style>
      /* Styling contract: override the public --chatbot-* properties from the
         host page (on #chatbot-widget or :root). The internal --_* values read
         them and fall back to the data-* attributes / sensible defaults, so the
         widget looks complete out of the box and the engine stays agnostic. */
      :host {
        all: initial;
        --_font: var(--chatbot-font, system-ui, sans-serif);
        --_accent: var(--chatbot-accent, ${cfg.accent});
        --_on-accent: var(--chatbot-on-accent, #fff);
        --_bg: var(--chatbot-bg, #fff);
        --_text: var(--chatbot-text, #111);
        --_bot-bg: var(--chatbot-bot-bg, #f0f0f0);
        --_bot-text: var(--chatbot-bot-text, #111);
        --_radius: var(--chatbot-radius, 12px);
        --_input-radius: var(--chatbot-input-radius, 8px);
        --_width: var(--chatbot-width, 380px);
        --_launcher: var(--chatbot-launcher-size, 56px);
        --_logo-h: var(--chatbot-logo-height, 24px);
        --_title-size: var(--chatbot-title-size, 16px);
      }
      * { box-sizing: border-box; font-family: var(--_font); }
      .launcher {
        position: fixed; bottom: 24px; ${cfg.position}: 24px;
        width: var(--_launcher); height: var(--_launcher); border-radius: 50%; border: none;
        background: var(--_accent); color: var(--_on-accent); font-size: 24px; cursor: pointer;
        box-shadow: 0 4px 16px rgba(0,0,0,.25); z-index: 2147483646;
      }
      .panel {
        position: fixed; bottom: 0; ${cfg.position}: 0; top: 0;
        width: var(--_width); max-width: 100vw; background: var(--_bg);
        display: flex; flex-direction: column;
        box-shadow: -4px 0 24px rgba(0,0,0,.2);
        transform: translateX(${cfg.position === "right" ? "100%" : "-100%"});
        transition: transform .25s ease; z-index: 2147483647;
      }
      .panel.open { transform: translateX(0); }
      .head {
        background: var(--_accent); color: var(--_on-accent); padding: 16px;
        display: flex; justify-content: space-between; align-items: center;
      }
      .head h3 { margin: 0; font-size: var(--_title-size); }
      .head .logo { height: var(--_logo-h); width: auto; display: block; }
      .head button { background: none; border: none; color: var(--_on-accent); font-size: 20px; cursor: pointer; }
      .msgs { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 10px; }
      .msg { max-width: 80%; padding: 8px 12px; border-radius: var(--_radius); line-height: 1.4; white-space: pre-wrap; }
      .msg.user { align-self: flex-end; background: var(--_accent); color: var(--_on-accent); }
      .msg.bot { align-self: flex-start; background: var(--_bot-bg); color: var(--_bot-text); }
      .foot { display: flex; gap: 8px; padding: 12px; border-top: 1px solid #eee; }
      .foot input { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: var(--_input-radius); color: var(--_text); }
      .foot button { background: var(--_accent); color: var(--_on-accent); border: none; border-radius: var(--_input-radius); padding: 0 16px; cursor: pointer; }
      .fb { align-self: flex-start; display: flex; gap: 6px; margin: -4px 0 4px; }
      .fb button { background: none; border: none; cursor: pointer; font-size: 14px; opacity: .55; padding: 0; }
      .fb button:hover { opacity: 1; }
    </style>
    <button class="launcher" aria-label="Chat oeffnen">&#128172;</button>
    <div class="panel" role="dialog" aria-label="${cfg.title}">
      <div class="head">
        ${cfg.logo
          ? `<img class="logo" src="${cfg.logo}" alt="${cfg.title}" />`
          : `<h3>${cfg.title}</h3>`}
        <button class="close" aria-label="Schliessen">&times;</button>
      </div>
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

  // Thumbs up/down under a bot answer; sends a Langfuse score for that turn.
  function addFeedback(traceId) {
    const bar = document.createElement("div");
    bar.className = "fb";
    for (const [icon, score] of [["\u{1F44D}", 1], ["\u{1F44E}", -1]]) {
      const b = document.createElement("button");
      b.textContent = icon;
      b.onclick = () => {
        fetch(cfg.api + "/feedback", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ trace_id: traceId, score }),
        });
        bar.remove();
      };
      bar.appendChild(b);
    }
    msgs.appendChild(bar);
    msgs.scrollTop = msgs.scrollHeight;
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
          } else if (evt.type === "done") {
            if (evt.trace_id) addFeedback(evt.trace_id);
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
