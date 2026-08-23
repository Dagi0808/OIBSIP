from flask import Flask, render_template_string, request, session, redirect, url_for

from src.assistant import get_response

app = Flask(__name__)
app.secret_key = "voice-assistant-session-key"

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Voice Assistant</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg: #0f0f10;
      --sidebar-bg: #171718;
      --chat-bg: #1a1a1b;
      --input-bg: #2a2a2b;
      --border: #2e2e30;
      --primary: #10a37f;
      --primary-hover: #0d8c6d;
      --user-bubble: #2a2a2b;
      --assistant-bubble: transparent;
      --text: #ececec;
      --text-muted: #8e8ea0;
      --chip-bg: #2a2a2b;
      --chip-border: #3e3e42;
      --chip-hover: #3a3a3c;
      --scrollbar: #3e3e42;
    }

    /* Light theme */
    :root.light {
      --bg: #f7f7f8;
      --sidebar-bg: #ffffff;
      --chat-bg: #ffffff;
      --input-bg: #f4f4f5;
      --border: #e5e5e7;
      --primary: #10a37f;
      --primary-hover: #0d8c6d;
      --user-bubble: #f0f0f1;
      --assistant-bubble: transparent;
      --text: #1a1a1b;
      --text-muted: #6e6e80;
      --chip-bg: #f4f4f5;
      --chip-border: #e5e5e7;
      --chip-hover: #ebebec;
      --scrollbar: #d0d0d5;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      height: 100vh;
      display: flex;
      overflow: hidden;
    }

    /* ── Sidebar ── */
    .sidebar {
      width: 260px;
      min-width: 260px;
      background: var(--sidebar-bg);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      padding: 16px 12px;
      gap: 8px;
    }

    .sidebar-logo {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 12px;
      margin-bottom: 8px;
    }

    .logo-icon {
      width: 32px;
      height: 32px;
      background: var(--primary);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      flex-shrink: 0;
    }

    .logo-text {
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--text);
    }

    .new-chat-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px 12px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: transparent;
      color: var(--text);
      cursor: pointer;
      font-size: 0.9rem;
      transition: background 0.15s;
      width: 100%;
      text-align: left;
    }

    .new-chat-btn:hover { background: var(--chip-hover); }

    .sidebar-section {
      font-size: 0.72rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.06em;
      padding: 8px 12px 4px;
    }

    .sidebar-item {
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 0.875rem;
      color: var(--text-muted);
      cursor: pointer;
      transition: background 0.15s, color 0.15s;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .sidebar-item:hover, .sidebar-item.active {
      background: var(--chip-hover);
      color: var(--text);
    }

    .sidebar-bottom {
      margin-top: auto;
      border-top: 1px solid var(--border);
      padding-top: 12px;
    }

    .sidebar-bottom .sidebar-item { color: var(--text-muted); }

    /* ── Main chat area ── */
    .main {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-width: 0;
      background: var(--chat-bg);
    }

    /* Header */
    .chat-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 24px;
      border-bottom: 1px solid var(--border);
      flex-shrink: 0;
    }

    .chat-title {
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--text);
    }

    .header-actions {
      display: flex;
      gap: 8px;
    }

    .lang-select {
      background: var(--chip-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--text);
      font-size: 0.8rem;
      padding: 5px 8px;
      cursor: pointer;
      outline: none;
      transition: border-color 0.2s;
      font-family: inherit;
    }
    .lang-select:focus { border-color: var(--primary); }
    .lang-select option { background: var(--sidebar-bg); }

    .icon-btn {
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      padding: 6px;
      border-radius: 6px;
      font-size: 1rem;
      transition: background 0.15s, color 0.15s;
    }

    .icon-btn:hover { background: var(--chip-hover); color: var(--text); }

    /* Messages */
    .messages {
      flex: 1;
      overflow-y: auto;
      padding: 24px 0;
      scroll-behavior: smooth;
    }

    .messages::-webkit-scrollbar { width: 6px; }
    .messages::-webkit-scrollbar-track { background: transparent; }
    .messages::-webkit-scrollbar-thumb { background: var(--scrollbar); border-radius: 3px; }

    /* Welcome screen */
    .welcome {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      gap: 16px;
      padding: 40px 24px;
    }

    .welcome-icon {
      width: 56px;
      height: 56px;
      background: var(--primary);
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 28px;
    }

    .welcome h2 {
      font-size: 1.6rem;
      font-weight: 700;
      color: var(--text);
    }

    .welcome p {
      font-size: 0.95rem;
      color: var(--text-muted);
      text-align: center;
      max-width: 420px;
    }

    .suggestions {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
      max-width: 560px;
      width: 100%;
      margin-top: 8px;
    }

    .suggestion-card {
      background: var(--chip-bg);
      border: 1px solid var(--chip-border);
      border-radius: 12px;
      padding: 14px 16px;
      cursor: pointer;
      transition: background 0.15s, border-color 0.15s;
      text-align: left;
    }

    .suggestion-card:hover {
      background: var(--chip-hover);
      border-color: var(--primary);
    }

    .suggestion-card .suggestion-title {
      font-size: 0.875rem;
      font-weight: 500;
      color: var(--text);
      margin-bottom: 4px;
    }

    .suggestion-card .suggestion-sub {
      font-size: 0.78rem;
      color: var(--text-muted);
    }

    /* Message bubbles */
    .message-row {
      display: flex;
      padding: 6px 24px;
      gap: 14px;
      max-width: 820px;
      margin: 0 auto;
      width: 100%;
    }

    .message-row.user { flex-direction: row-reverse; }

    .avatar {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      font-weight: 700;
      margin-top: 2px;
    }

    .avatar.user-avatar {
      background: #5c5fff;
      color: white;
    }

    .avatar.assistant-avatar {
      background: var(--primary);
      color: white;
    }

    .bubble {
      max-width: 75%;
      padding: 12px 16px;
      border-radius: 16px;
      font-size: 0.925rem;
      line-height: 1.6;
      white-space: pre-wrap;
      word-break: break-word;
    }

    .message-row.user .bubble {
      background: var(--user-bubble);
      border: 1px solid var(--border);
      border-bottom-right-radius: 4px;
      color: var(--text);
    }

    .message-row.assistant .bubble {
      background: var(--assistant-bubble);
      color: var(--text);
      border-bottom-left-radius: 4px;
    }

    .message-meta {
      font-size: 0.72rem;
      color: var(--text-muted);
      margin-top: 4px;
      padding: 0 4px;
    }

    .message-row.user .message-meta { text-align: right; }

    /* Quick chips bar */
    .chips-bar {
      padding: 10px 24px;
      border-top: 1px solid var(--border);
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      flex-shrink: 0;
    }

    .chip {
      background: var(--chip-bg);
      border: 1px solid var(--chip-border);
      color: var(--text-muted);
      border-radius: 999px;
      padding: 6px 14px;
      font-size: 0.8rem;
      cursor: pointer;
      transition: background 0.15s, color 0.15s, border-color 0.15s;
      white-space: nowrap;
    }

    .chip:hover {
      background: var(--chip-hover);
      color: var(--text);
      border-color: var(--primary);
    }

    /* Input area */
    .input-area {
      padding: 12px 24px 20px;
      flex-shrink: 0;
    }

    .input-box {
      display: flex;
      align-items: flex-end;
      gap: 8px;
      background: var(--input-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 10px 12px;
      transition: border-color 0.2s;
    }

    .input-box:focus-within {
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.12);
    }

    #command {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      color: var(--text);
      font-size: 0.95rem;
      resize: none;
      max-height: 160px;
      min-height: 24px;
      line-height: 1.5;
      padding: 2px 0;
      font-family: inherit;
    }

    #command::placeholder { color: var(--text-muted); }

    .input-actions {
      display: flex;
      gap: 6px;
      align-items: center;
      flex-shrink: 0;
    }

    .send-btn {
      width: 34px;
      height: 34px;
      background: var(--primary);
      border: none;
      border-radius: 8px;
      color: white;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      transition: background 0.15s, transform 0.1s;
      flex-shrink: 0;
    }

    .send-btn:hover { background: var(--primary-hover); transform: scale(1.05); }
    .send-btn:disabled { background: var(--border); cursor: not-allowed; transform: none; }

    .mic-btn {
      width: 34px;
      height: 34px;
      background: transparent;
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--text-muted);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      transition: background 0.15s, color 0.15s, border-color 0.15s;
      flex-shrink: 0;
    }

    .mic-btn:hover { background: var(--chip-hover); color: var(--text); border-color: var(--primary); }
    .mic-btn.listening { background: #e63946; border-color: #e63946; color: white; animation: pulse 1s infinite; }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.6; }
    }

    .input-hint {
      font-size: 0.72rem;
      color: var(--text-muted);
      text-align: center;
      margin-top: 8px;
    }

    /* Responsive */
    .typing-indicator {
      display: flex;
      gap: 4px;
      align-items: center;
      padding: 12px 16px;
    }

    .typing-dot {
      width: 7px;
      height: 7px;
      background: var(--text-muted);
      border-radius: 50%;
      animation: bounce 1.2s infinite;
    }

    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes bounce {
      0%, 80%, 100% { transform: translateY(0); }
      40% { transform: translateY(-6px); }
    }

    /* ── Email setup modal ── */
    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(4px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 100;
      padding: 20px;
    }

    .modal {
      background: var(--sidebar-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 28px;
      max-width: 440px;
      width: 100%;
      box-shadow: 0 24px 60px rgba(0,0,0,0.4);
    }

    .modal-header {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;
    }

    .modal-icon {
      font-size: 28px;
    }

    .modal h3 {
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--text);
    }

    .modal p {
      font-size: 0.875rem;
      color: var(--text-muted);
      line-height: 1.6;
      margin-bottom: 20px;
    }

    .security-badge {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      background: rgba(16, 163, 127, 0.1);
      border: 1px solid rgba(16, 163, 127, 0.25);
      border-radius: 10px;
      padding: 12px 14px;
      margin-bottom: 20px;
      font-size: 0.8rem;
      color: var(--text-muted);
      line-height: 1.5;
    }

    .security-badge .shield {
      font-size: 18px;
      flex-shrink: 0;
      margin-top: 1px;
    }

    .security-badge strong {
      display: block;
      color: #10a37f;
      margin-bottom: 2px;
      font-size: 0.82rem;
    }

    .form-group {
      margin-bottom: 14px;
    }

    .form-group label {
      display: block;
      font-size: 0.82rem;
      font-weight: 500;
      color: var(--text-muted);
      margin-bottom: 6px;
    }

    .form-group input {
      width: 100%;
      padding: 10px 14px;
      background: var(--input-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      color: var(--text);
      font-size: 0.9rem;
      outline: none;
      transition: border-color 0.2s;
      font-family: inherit;
    }

    .form-group input:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(16, 163, 127, 0.12);
    }

    .form-group input::placeholder { color: var(--text-muted); }

    .form-hint {
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-top: 5px;
    }

    .form-hint a {
      color: var(--primary);
      text-decoration: none;
    }

    .form-hint a:hover { text-decoration: underline; }

    .modal-actions {
      display: flex;
      gap: 10px;
      margin-top: 20px;
    }

    .btn-primary {
      flex: 1;
      padding: 10px 16px;
      background: var(--primary);
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.15s;
    }

    .btn-primary:hover { background: var(--primary-hover); }

    .btn-secondary {
      padding: 10px 16px;
      background: transparent;
      color: var(--text-muted);
      border: 1px solid var(--border);
      border-radius: 8px;
      font-size: 0.9rem;
      cursor: pointer;
      transition: background 0.15s, color 0.15s;
    }

    .btn-secondary:hover { background: var(--chip-hover); color: var(--text); }

    .error-msg {
      background: rgba(230, 57, 70, 0.12);
      border: 1px solid rgba(230, 57, 70, 0.3);
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 0.82rem;
      color: #e63946;
      margin-bottom: 16px;
    }
    @media (max-width: 640px) {
      .sidebar { display: none; }
      .suggestions { grid-template-columns: 1fr; }
      .bubble { max-width: 90%; }
    }
  </style>
</head>
<body>

  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="sidebar-logo">
      <div class="logo-icon">🤖</div>
      <span class="logo-text">Voice Assistant</span>
    </div>

    <form method="POST" style="margin:0">
      <input type="hidden" name="new_chat" value="1">
      <button type="submit" class="new-chat-btn">
        <span>✏️</span> New chat
      </button>
    </form>

    <div class="sidebar-section">Suggestions</div>
    <div class="sidebar-item" onclick="fillInput('who is Albert Einstein')">🧠 Who is Einstein?</div>
    <div class="sidebar-item" onclick="fillInput('what is the weather in Addis Ababa')">🌤️ Weather check</div>
    <div class="sidebar-item" onclick="fillInput('remind me in 5 minutes to drink water')">⏰ Set a reminder</div>
    <div class="sidebar-item" onclick="fillInput('search for Python tutorials')">🔍 Web search</div>

    <div class="sidebar-bottom">
      <div class="sidebar-item">⚙️ Settings</div>
      <div class="sidebar-item">❓ Help</div>
    </div>
  </aside>

  <!-- Main -->
  <main class="main">

    <!-- Header -->
    <div class="chat-header">
      <span class="chat-title">Voice Assistant</span>
      <div class="header-actions">
        <select class="lang-select" id="lang-select" title="Speech language" onchange="saveLang(this.value)">
          <option value="en-US">🇺🇸 English (US)</option>
          <option value="en-GB">🇬🇧 English (UK)</option>
          <option value="am-ET">🇪🇹 Amharic</option>
          <option value="fr-FR">🇫🇷 French</option>
          <option value="ar-SA">🇸🇦 Arabic</option>
          <option value="es-ES">🇪🇸 Spanish</option>
          <option value="de-DE">🇩🇪 German</option>
          <option value="zh-CN">🇨🇳 Chinese</option>
        </select>
        <button class="icon-btn" title="Toggle theme" id="theme-toggle" onclick="toggleTheme()">🌙</button>
        <button class="icon-btn" title="Clear chat" onclick="clearChat()">🗑️</button>
        <button class="icon-btn" id="tts-toggle" title="Toggle voice responses" onclick="toggleTTS()">🔊</button>
      </div>
    </div>

    <!-- Messages -->
    <div class="messages" id="messages">
      {% if not history %}
      <div class="welcome" id="welcome-screen">
        <div class="welcome-icon">🤖</div>
        <h2>How can I help you?</h2>
        <p>Ask me about the weather, set a reminder, search the web, or learn something new.</p>
        <div class="suggestions">
          <div class="suggestion-card" onclick="fillInput('what is the weather in Addis Ababa')">
            <div class="suggestion-title">🌤️ Weather</div>
            <div class="suggestion-sub">What's the weather in Addis Ababa?</div>
          </div>
          <div class="suggestion-card" onclick="fillInput('remind me in 5 minutes to drink water')">
            <div class="suggestion-title">⏰ Reminder</div>
            <div class="suggestion-sub">Remind me in 5 minutes to drink water</div>
          </div>
          <div class="suggestion-card" onclick="fillInput('who is Albert Einstein')">
            <div class="suggestion-title">🧠 Knowledge</div>
            <div class="suggestion-sub">Who is Albert Einstein?</div>
          </div>
          <div class="suggestion-card" onclick="fillInput('search for Python tutorials')">
            <div class="suggestion-title">🔍 Search</div>
            <div class="suggestion-sub">Search for Python tutorials</div>
          </div>
        </div>
      </div>
      {% else %}
        {% for msg in history %}
        <div class="message-row {{ msg.role }}">
          <div class="avatar {{ msg.role }}-avatar">
            {% if msg.role == 'user' %}D{% else %}🤖{% endif %}
          </div>
          <div>
            <div class="bubble">{{ msg.text }}</div>
            <div class="message-meta">{{ msg.time }}</div>
          </div>
        </div>
        {% endfor %}
      {% endif %}
    </div>

    <!-- Quick chips -->
    <div class="chips-bar">
      <button class="chip" onclick="fillInput('hello')">👋 hello</button>
      <button class="chip" onclick="fillInput('what time is it')">🕐 time</button>
      <button class="chip" onclick="fillInput('what date is it')">📅 date</button>
      <button class="chip" onclick="fillInput('what is the weather in Addis Ababa')">🌤️ weather</button>
      <button class="chip" onclick="fillInput('search for Python tutorials')">🔍 search</button>
      <button class="chip" onclick="fillInput('remind me in 1 minutes to drink water')">⏰ reminder</button>
      <button class="chip" onclick="fillInput('who is Albert Einstein')">🧠 knowledge</button>
      <button class="chip" onclick="fillInput('open my notes')">📂 open</button>
    </div>

    <!-- Input -->
    <div class="input-area">
      <form method="POST" id="chat-form" accept-charset="utf-8">
        <div class="input-box">
          <textarea id="command" name="command" placeholder="Message Voice Assistant..." rows="1" required></textarea>
          <div class="input-actions">
            <button type="button" class="mic-btn" id="mic-btn" title="Speak">🎙️</button>
            <button type="submit" class="send-btn" id="send-btn" title="Send">
              ➤
            </button>
          </div>
        </div>
      </form>
      <div class="input-hint" id="status-text">Press Enter to send · Click 🎙️ to speak</div>
    </div>

  </main>

  <script>
    // ── Language selector ──
    const langSelect = document.getElementById('lang-select');
    let currentLang = localStorage.getItem('va-lang') || 'en-US';
    langSelect.value = currentLang;
    function saveLang(v) { currentLang = v; localStorage.setItem('va-lang', v); }

    // ── Theme toggle ──
    const root = document.documentElement;
    const themeBtn = document.getElementById('theme-toggle');

    function applyTheme(theme) {
      if (theme === 'light') {
        root.classList.add('light');
        themeBtn.textContent = '☀️';
        themeBtn.title = 'Switch to dark mode';
      } else {
        root.classList.remove('light');
        themeBtn.textContent = '🌙';
        themeBtn.title = 'Switch to light mode';
      }
    }

    function toggleTheme() {
      const current = root.classList.contains('light') ? 'light' : 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      localStorage.setItem('va-theme', next);
      applyTheme(next);
    }

    // Apply saved theme on load
    applyTheme(localStorage.getItem('va-theme') || 'dark');

    // ── Auto-resize textarea ──
    const textarea = document.getElementById('command');
    textarea.addEventListener('input', function () {
      this.style.height = 'auto';
      this.style.height = Math.min(this.scrollHeight, 160) + 'px';
    });

    // Submit on Enter (Shift+Enter for newline)
    textarea.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        document.getElementById('chat-form').submit();
      }
    });

    // ── Fill input from chips/suggestions ──
    function fillInput(text) {
      textarea.value = text;
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 160) + 'px';
      textarea.focus();
    }

    // ── Scroll to bottom ──
    function scrollToBottom() {
      const messages = document.getElementById('messages');
      messages.scrollTop = messages.scrollHeight;
    }
    scrollToBottom();

    // ── Clear chat ──
    function clearChat() {
      const form = document.createElement('form');
      form.method = 'POST';
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'new_chat';
      input.value = '1';
      form.appendChild(input);
      document.body.appendChild(form);
      form.submit();
    }

    // ── TTS toggle ──
    let ttsEnabled = true;
    function toggleTTS() {
      ttsEnabled = !ttsEnabled;
      document.getElementById('tts-toggle').textContent = ttsEnabled ? '🔊' : '🔇';
    }

    function speakResponse(text) {
      if (!ttsEnabled || !('speechSynthesis' in window)) return;
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = currentLang;
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utterance);
    }

    // Speak the latest assistant response on page load
    {% if history %}
      {% set last = history[-1] %}
      {% if last.role == 'assistant' %}
        window.addEventListener('load', function() {
          speakResponse({{ last.text | tojson }});
        });
      {% endif %}
    {% endif %}

    // ── Speech recognition ──
    const micBtn = document.getElementById('mic-btn');
    const statusText = document.getElementById('status-text');
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.lang = currentLang;
      recognition.continuous = false;

      recognition.onstart = function () {
        micBtn.classList.add('listening');
        statusText.textContent = '🎙️ Listening...';
      };

      recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        textarea.value = transcript;
        statusText.textContent = 'Command captured. Sending...';
        document.getElementById('chat-form').submit();
      };

      recognition.onend = function () {
        micBtn.classList.remove('listening');
        statusText.textContent = 'Press Enter to send · Click 🎙️ to speak';
      };

      recognition.onerror = function (event) {
        micBtn.classList.remove('listening');
        statusText.textContent = 'Mic error: ' + event.error;
      };

      micBtn.addEventListener('click', function () {
        recognition.lang = currentLang;
        recognition.start();
      });
    } else {
      micBtn.disabled = true;
      micBtn.title = 'Speech not supported in this browser';
      statusText.textContent = 'Speech recognition not available. Use Chrome or Edge.';
    }
  </script>

  <!-- Email setup modal -->
  {% if show_email_modal %}
  <div class="modal-overlay" id="email-modal">
    <div class="modal">
      <div class="modal-header">
        <div class="modal-icon">📧</div>
        <h3>Connect your Gmail</h3>
      </div>
      <p>To read your emails, enter your Gmail address and a Gmail App Password below.</p>

      <div class="security-badge">
        <span class="shield">🔒</span>
        <div>
          <strong>Your credentials are safe</strong>
          Your email and password are stored only in your browser session — never saved to disk, never sent anywhere except directly to Gmail's servers. They are cleared when you close the tab or start a new chat.
        </div>
      </div>

      {% if email_error %}
      <div class="error-msg">
        {% if email_error == 'auth' %}
          ❌ Login failed. Check your email address and App Password.
        {% elif email_error == 'connect' %}
          ❌ Could not connect to Gmail. Check your internet connection.
        {% else %}
          ❌ Something went wrong. Please try again.
        {% endif %}
      </div>
      {% endif %}

      <form method="POST" id="email-form">
        <input type="hidden" name="email_setup" value="1">
        <div class="form-group">
          <label for="user_email">Gmail address</label>
          <input type="email" id="user_email" name="user_email" placeholder="you@gmail.com" required autocomplete="email">
        </div>
        <div class="form-group">
          <label for="user_app_password">Gmail App Password</label>
          <input type="password" id="user_app_password" name="user_app_password" placeholder="xxxx xxxx xxxx xxxx" required autocomplete="off">
          <div class="form-hint">
            This is a 16-character App Password, not your Gmail login password.
            <a href="https://myaccount.google.com/apppasswords" target="_blank" rel="noopener">Get one here →</a>
          </div>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn-secondary" onclick="dismissModal()">Cancel</button>
          <button type="submit" class="btn-primary">🔐 Connect & Read Inbox</button>
        </div>
      </form>
    </div>
  </div>
  {% endif %}

  <script>
    function dismissModal() {
      const modal = document.getElementById('email-modal');
      if (modal) modal.style.display = 'none';
    }
  </script>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    from src.email_service import read_inbox
    from datetime import datetime

    if "history" not in session:
        session["history"] = []

    # Read flash values set during a previous POST redirect
    show_email_modal = session.pop("_show_email_modal", False)
    email_error = session.pop("_email_error", None)

    if request.method == "POST":

        # Clear chat
        if request.form.get("new_chat"):
            session.clear()
            session.modified = True
            return redirect(url_for("index"))

        # Email setup
        if request.form.get("email_setup"):
            user_email = request.form.get("user_email", "").strip()
            user_pw = request.form.get("user_app_password", "").strip()
            now = datetime.now().strftime("%I:%M %p")
            result = read_inbox(user_email, user_pw)

            if result == "EMAIL_AUTH_FAILED":
                session["_show_email_modal"] = True
                session["_email_error"] = "auth"
            elif result == "EMAIL_CONNECT_FAILED":
                session["_show_email_modal"] = True
                session["_email_error"] = "connect"
            else:
                session["user_email"] = user_email
                session["user_app_password"] = user_pw
                history = session.get("history", [])
                history.append({"role": "user", "text": "check my email", "time": now})
                history.append({"role": "assistant", "text": result, "time": now})
                session["history"] = history[-40:]

            session.modified = True
            return redirect(url_for("index"))

        # Normal command
        command = request.form.get("command", "").strip()
        if command:
            now = datetime.now().strftime("%I:%M %p")
            history = session.get("history", [])
            history.append({"role": "user", "text": command, "time": now})

            response = get_response(command)

            if response == "EMAIL_SETUP_NEEDED":
                if session.get("user_email") and session.get("user_app_password"):
                    response = read_inbox(session["user_email"], session["user_app_password"])
                    if response == "EMAIL_AUTH_FAILED":
                        session.pop("user_email", None)
                        session.pop("user_app_password", None)
                        response = "Your saved email credentials expired. Please reconnect."
                        session["_show_email_modal"] = True
                    elif response == "EMAIL_CONNECT_FAILED":
                        response = "I couldn't connect to Gmail right now."
                else:
                    session["_show_email_modal"] = True
                    response = "I need your Gmail credentials to check your inbox."

            history.append({"role": "assistant", "text": response, "time": now})
            session["history"] = history[-40:]
            session.modified = True

        return redirect(url_for("index"))

    return render_template_string(
        HTML,
        history=session.get("history", []),
        show_email_modal=show_email_modal,
        email_error=email_error,
    )


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
