from flask import Flask, jsonify, render_template_string, request, session

from src.assistant import get_response

app = Flask(__name__)
app.secret_key = "voice-assistant-session-key"

# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------
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
      --bg: #0f0f10; --sidebar-bg: #171718; --chat-bg: #1a1a1b;
      --input-bg: #2a2a2b; --border: #2e2e30; --primary: #10a37f;
      --primary-hover: #0d8c6d; --user-bubble: #2a2a2b;
      --text: #ececec; --text-muted: #8e8ea0;
      --chip-bg: #2a2a2b; --chip-border: #3e3e42; --chip-hover: #3a3a3c;
      --scrollbar: #3e3e42;
    }
    :root.light {
      --bg: #f7f7f8; --sidebar-bg: #ffffff; --chat-bg: #ffffff;
      --input-bg: #f4f4f5; --border: #e5e5e7; --primary: #10a37f;
      --primary-hover: #0d8c6d; --user-bubble: #f0f0f1;
      --text: #1a1a1b; --text-muted: #6e6e80;
      --chip-bg: #f4f4f5; --chip-border: #e5e5e7; --chip-hover: #ebebec;
      --scrollbar: #d0d0d5;
    }

    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
           background: var(--bg); color: var(--text); height: 100vh; display: flex; overflow: hidden; }

    /* Sidebar */
    .sidebar { width: 260px; min-width: 260px; background: var(--sidebar-bg);
               border-right: 1px solid var(--border); display: flex; flex-direction: column;
               padding: 16px 12px; gap: 8px; }
    .sidebar-logo { display: flex; align-items: center; gap: 10px; padding: 8px 12px; margin-bottom: 8px; }
    .logo-icon { width: 32px; height: 32px; background: var(--primary); border-radius: 8px;
                 display: flex; align-items: center; justify-content: center; font-size: 16px; }
    .logo-text { font-size: 0.95rem; font-weight: 600; color: var(--text); }
    .new-chat-btn { display: flex; align-items: center; gap: 8px; padding: 10px 12px;
                    border-radius: 8px; border: 1px solid var(--border); background: transparent;
                    color: var(--text); cursor: pointer; font-size: 0.9rem; width: 100%;
                    transition: background 0.15s; }
    .new-chat-btn:hover { background: var(--chip-hover); }
    .sidebar-section { font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase;
                       letter-spacing: 0.06em; padding: 8px 12px 4px; }
    .sidebar-item { padding: 8px 12px; border-radius: 8px; font-size: 0.875rem; color: var(--text-muted);
                    cursor: pointer; transition: background 0.15s, color 0.15s;
                    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .sidebar-item:hover { background: var(--chip-hover); color: var(--text); }
    .sidebar-bottom { margin-top: auto; border-top: 1px solid var(--border); padding-top: 12px; }

    /* Main */
    .main { flex: 1; display: flex; flex-direction: column; min-width: 0; background: var(--chat-bg); }
    .chat-header { display: flex; align-items: center; justify-content: space-between;
                   padding: 14px 24px; border-bottom: 1px solid var(--border); flex-shrink: 0; }
    .chat-title { font-size: 0.95rem; font-weight: 600; color: var(--text); }
    .header-actions { display: flex; gap: 8px; align-items: center; }
    .icon-btn { background: transparent; border: none; color: var(--text-muted); cursor: pointer;
                padding: 6px; border-radius: 6px; font-size: 1rem; transition: background 0.15s, color 0.15s; }
    .icon-btn:hover { background: var(--chip-hover); color: var(--text); }
    .lang-select { background: var(--chip-bg); border: 1px solid var(--border); border-radius: 8px;
                   color: var(--text); font-size: 0.8rem; padding: 5px 8px; cursor: pointer;
                   outline: none; font-family: inherit; }
    .lang-select option { background: var(--sidebar-bg); }

    /* Messages */
    .messages { flex: 1; overflow-y: auto; padding: 24px 0; scroll-behavior: smooth; }
    .messages::-webkit-scrollbar { width: 6px; }
    .messages::-webkit-scrollbar-thumb { background: var(--scrollbar); border-radius: 3px; }

    /* Welcome */
    .welcome { display: flex; flex-direction: column; align-items: center; justify-content: center;
               height: 100%; gap: 16px; padding: 40px 24px; }
    .welcome-icon { width: 56px; height: 56px; background: var(--primary); border-radius: 16px;
                    display: flex; align-items: center; justify-content: center; font-size: 28px; }
    .welcome h2 { font-size: 1.6rem; font-weight: 700; }
    .welcome p { font-size: 0.95rem; color: var(--text-muted); text-align: center; max-width: 420px; }
    .suggestions { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;
                   max-width: 560px; width: 100%; margin-top: 8px; }
    .suggestion-card { background: var(--chip-bg); border: 1px solid var(--chip-border);
                       border-radius: 12px; padding: 14px 16px; cursor: pointer;
                       transition: background 0.15s, border-color 0.15s; text-align: left; }
    .suggestion-card:hover { background: var(--chip-hover); border-color: var(--primary); }
    .suggestion-title { font-size: 0.875rem; font-weight: 500; margin-bottom: 4px; }
    .suggestion-sub { font-size: 0.78rem; color: var(--text-muted); }

    /* Bubbles */
    .message-row { display: flex; padding: 6px 24px; gap: 14px; max-width: 820px; margin: 0 auto; width: 100%; }
    .message-row.user { flex-direction: row-reverse; }
    .avatar { width: 32px; height: 32px; border-radius: 8px; flex-shrink: 0; display: flex;
               align-items: center; justify-content: center; font-size: 14px; font-weight: 700; margin-top: 2px; }
    .avatar.user-avatar { background: #5c5fff; color: white; }
    .avatar.assistant-avatar { background: var(--primary); color: white; }
    .bubble { max-width: 75%; padding: 12px 16px; border-radius: 16px; font-size: 0.925rem;
              line-height: 1.6; white-space: pre-wrap; word-break: break-word; }
    .message-row.user .bubble { background: var(--user-bubble); border: 1px solid var(--border);
                                 border-bottom-right-radius: 4px; }
    .message-row.assistant .bubble { border-bottom-left-radius: 4px; }
    .message-meta { font-size: 0.72rem; color: var(--text-muted); margin-top: 4px; padding: 0 4px; }
    .message-row.user .message-meta { text-align: right; }

    /* Chips */
    .chips-bar { padding: 10px 24px; border-top: 1px solid var(--border); display: flex;
                 gap: 8px; flex-wrap: wrap; flex-shrink: 0; }
    .chip { background: var(--chip-bg); border: 1px solid var(--chip-border); color: var(--text-muted);
            border-radius: 999px; padding: 6px 14px; font-size: 0.8rem; cursor: pointer;
            transition: background 0.15s, color 0.15s, border-color 0.15s; white-space: nowrap; }
    .chip:hover { background: var(--chip-hover); color: var(--text); border-color: var(--primary); }

    /* Input */
    .input-area { padding: 12px 24px 20px; flex-shrink: 0; }
    .input-box { display: flex; align-items: flex-end; gap: 8px; background: var(--input-bg);
                 border: 1px solid var(--border); border-radius: 14px; padding: 10px 12px;
                 transition: border-color 0.2s; }
    .input-box:focus-within { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(16,163,127,0.12); }
    #command { flex: 1; background: transparent; border: none; outline: none; color: var(--text);
               font-size: 0.95rem; resize: none; max-height: 160px; min-height: 24px;
               line-height: 1.5; padding: 2px 0; font-family: inherit; }
    #command::placeholder { color: var(--text-muted); }
    .input-actions { display: flex; gap: 6px; align-items: center; flex-shrink: 0; }
    .send-btn { width: 34px; height: 34px; background: var(--primary); border: none; border-radius: 8px;
                color: white; cursor: pointer; display: flex; align-items: center; justify-content: center;
                font-size: 14px; transition: background 0.15s, transform 0.1s; }
    .send-btn:hover { background: var(--primary-hover); transform: scale(1.05); }
    .send-btn:disabled { background: var(--border); cursor: not-allowed; transform: none; }
    .mic-btn { width: 34px; height: 34px; background: transparent; border: 1px solid var(--border);
               border-radius: 8px; color: var(--text-muted); cursor: pointer; display: flex;
               align-items: center; justify-content: center; font-size: 14px;
               transition: background 0.15s, color 0.15s, border-color 0.15s; }
    .mic-btn:hover { background: var(--chip-hover); color: var(--text); border-color: var(--primary); }
    .mic-btn.listening { background: #e63946; border-color: #e63946; color: white; animation: pulse 1s infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.6} }
    .input-hint { font-size: 0.72rem; color: var(--text-muted); text-align: center; margin-top: 8px; }

    /* Modal */
    .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px);
                     display: none; align-items: center; justify-content: center; z-index: 100; padding: 20px; }
    .modal-overlay.open { display: flex; }
    .modal { background: var(--sidebar-bg); border: 1px solid var(--border); border-radius: 16px;
             padding: 28px; max-width: 440px; width: 100%; box-shadow: 0 24px 60px rgba(0,0,0,0.4); }
    .modal-header { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
    .modal-icon { font-size: 28px; }
    .modal h3 { font-size: 1.1rem; font-weight: 700; }
    .modal p { font-size: 0.875rem; color: var(--text-muted); line-height: 1.6; margin-bottom: 20px; }
    .security-badge { display: flex; align-items: flex-start; gap: 10px;
                      background: rgba(16,163,127,0.1); border: 1px solid rgba(16,163,127,0.25);
                      border-radius: 10px; padding: 12px 14px; margin-bottom: 20px;
                      font-size: 0.8rem; color: var(--text-muted); line-height: 1.5; }
    .security-badge .shield { font-size: 18px; flex-shrink: 0; }
    .security-badge strong { display: block; color: #10a37f; margin-bottom: 2px; font-size: 0.82rem; }
    .form-group { margin-bottom: 14px; }
    .form-group label { display: block; font-size: 0.82rem; font-weight: 500;
                        color: var(--text-muted); margin-bottom: 6px; }
    .form-group input { width: 100%; padding: 10px 14px; background: var(--input-bg);
                        border: 1px solid var(--border); border-radius: 8px; color: var(--text);
                        font-size: 0.9rem; outline: none; font-family: inherit; }
    .form-group input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(16,163,127,0.12); }
    .form-group input::placeholder { color: var(--text-muted); }
    .form-hint { font-size: 0.75rem; color: var(--text-muted); margin-top: 5px; }
    .form-hint a { color: var(--primary); text-decoration: none; }
    .modal-actions { display: flex; gap: 10px; margin-top: 20px; }
    .btn-primary { flex: 1; padding: 10px 16px; background: var(--primary); color: white; border: none;
                   border-radius: 8px; font-size: 0.9rem; font-weight: 600; cursor: pointer; }
    .btn-primary:hover { background: var(--primary-hover); }
    .btn-secondary { padding: 10px 16px; background: transparent; color: var(--text-muted);
                     border: 1px solid var(--border); border-radius: 8px; font-size: 0.9rem; cursor: pointer; }
    .btn-secondary:hover { background: var(--chip-hover); color: var(--text); }
    .error-msg { background: rgba(230,57,70,0.12); border: 1px solid rgba(230,57,70,0.3);
                 border-radius: 8px; padding: 10px 14px; font-size: 0.82rem; color: #e63946;
                 margin-bottom: 16px; display: none; }

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
  <button class="new-chat-btn" onclick="clearChat()"><span>✏️</span> New chat</button>
  <div class="sidebar-section">Suggestions</div>
  <div class="sidebar-item" onclick="fillAndSend('who is Albert Einstein')">🧠 Who is Einstein?</div>
  <div class="sidebar-item" onclick="fillAndSend('what is the weather in Addis Ababa')">🌤️ Weather check</div>
  <div class="sidebar-item" onclick="fillAndSend('remind me in 5 minutes to drink water')">⏰ Set a reminder</div>
  <div class="sidebar-item" onclick="fillAndSend('search for Python tutorials')">🔍 Web search</div>
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
      <select class="lang-select" id="lang-select" onchange="saveLang(this.value)">
        <option value="en-US">🇺🇸 English (US)</option>
        <option value="en-GB">🇬🇧 English (UK)</option>
        <option value="am-ET">🇪🇹 Amharic</option>
        <option value="fr-FR">🇫🇷 French</option>
        <option value="ar-SA">🇸🇦 Arabic</option>
        <option value="es-ES">🇪🇸 Spanish</option>
        <option value="de-DE">🇩🇪 German</option>
        <option value="zh-CN">🇨🇳 Chinese</option>
      </select>
      <button class="icon-btn" id="theme-btn" onclick="toggleTheme()" title="Toggle theme">🌙</button>
      <button class="icon-btn" onclick="clearChat()" title="Clear chat">🗑️</button>
      <button class="icon-btn" id="tts-btn" onclick="toggleTTS()" title="Toggle voice">🔊</button>
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
        <div class="suggestion-card" onclick="fillAndSend('what is the weather in Addis Ababa')">
          <div class="suggestion-title">🌤️ Weather</div>
          <div class="suggestion-sub">What's the weather in Addis Ababa?</div>
        </div>
        <div class="suggestion-card" onclick="fillAndSend('remind me in 5 minutes to drink water')">
          <div class="suggestion-title">⏰ Reminder</div>
          <div class="suggestion-sub">Remind me in 5 minutes to drink water</div>
        </div>
        <div class="suggestion-card" onclick="fillAndSend('who is Albert Einstein')">
          <div class="suggestion-title">🧠 Knowledge</div>
          <div class="suggestion-sub">Who is Albert Einstein?</div>
        </div>
        <div class="suggestion-card" onclick="fillAndSend('search for Python tutorials')">
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

  <!-- Chips -->
  <div class="chips-bar">
    <button class="chip" onclick="fillAndSend('hello')">👋 hello</button>
    <button class="chip" onclick="fillAndSend('what time is it')">🕐 time</button>
    <button class="chip" onclick="fillAndSend('what date is it')">📅 date</button>
    <button class="chip" onclick="fillAndSend('what is the weather in Addis Ababa')">🌤️ weather</button>
    <button class="chip" onclick="fillAndSend('search for Python tutorials')">🔍 search</button>
    <button class="chip" onclick="fillAndSend('remind me in 1 minutes to drink water')">⏰ reminder</button>
    <button class="chip" onclick="fillAndSend('who is Albert Einstein')">🧠 knowledge</button>
    <button class="chip" onclick="fillAndSend('open my notes')">📂 open</button>
  </div>

  <!-- Input -->
  <div class="input-area">
    <div class="input-box">
      <textarea id="command" placeholder="Message Voice Assistant..." rows="1"></textarea>
      <div class="input-actions">
        <button class="mic-btn" id="mic-btn" type="button" title="Speak">🎙️</button>
        <button class="send-btn" id="send-btn" type="button" onclick="submitChat()">➤</button>
      </div>
    </div>
    <div class="input-hint" id="status-text">Press Enter to send · Click 🎙️ to speak</div>
  </div>
</main>

<!-- Email modal -->
<div class="modal-overlay" id="email-modal">
  <div class="modal">
    <div class="modal-header">
      <div class="modal-icon">📧</div>
      <h3>Connect your Gmail</h3>
    </div>
    <p>Enter your Gmail address and a Gmail App Password to read your inbox.</p>
    <div class="security-badge">
      <span class="shield">🔒</span>
      <div>
        <strong>Your credentials are safe</strong>
        Stored only in your browser session — never saved to disk, never sent anywhere except directly to Gmail's servers. Cleared when you close the tab or start a new chat.
      </div>
    </div>
    <div class="error-msg" id="email-error"></div>
    <div class="form-group">
      <label for="user_email">Gmail address</label>
      <input type="email" id="user_email" placeholder="you@gmail.com" autocomplete="email">
    </div>
    <div class="form-group">
      <label for="user_pw">Gmail App Password</label>
      <input type="password" id="user_pw" placeholder="xxxx xxxx xxxx xxxx" autocomplete="off">
      <div class="form-hint">
        16-character App Password (not your Gmail login password).
        <a href="https://myaccount.google.com/apppasswords" target="_blank" rel="noopener">Get one here →</a>
      </div>
    </div>
    <div class="modal-actions">
      <button class="btn-secondary" onclick="closeEmailModal()">Cancel</button>
      <button class="btn-primary" id="email-submit-btn" onclick="submitEmail()">🔐 Connect & Read Inbox</button>
    </div>
  </div>
</div>

<script>
  // ── Globals ──
  const textarea   = document.getElementById('command');
  const messagesDiv = document.getElementById('messages');
  const sendBtn    = document.getElementById('send-btn');
  const statusText = document.getElementById('status-text');
  const micBtn     = document.getElementById('mic-btn');
  const themeBtn   = document.getElementById('theme-btn');
  const ttsBtn     = document.getElementById('tts-btn');
  const langSelect = document.getElementById('lang-select');
  let ttsEnabled   = true;
  let currentLang  = localStorage.getItem('va-lang') || 'en-US';

  // ── Init on load ──
  langSelect.value = currentLang;
  applyTheme(localStorage.getItem('va-theme') || 'dark');
  scrollBottom();

  // ── Language ──
  function saveLang(v) { currentLang = v; localStorage.setItem('va-lang', v); }

  // ── Theme ──
  function applyTheme(t) {
    if (t === 'light') { document.documentElement.classList.add('light'); themeBtn.textContent = '☀️'; }
    else               { document.documentElement.classList.remove('light'); themeBtn.textContent = '🌙'; }
  }
  function toggleTheme() {
    const next = document.documentElement.classList.contains('light') ? 'dark' : 'light';
    localStorage.setItem('va-theme', next); applyTheme(next);
  }

  // ── TTS ──
  function toggleTTS() { ttsEnabled = !ttsEnabled; ttsBtn.textContent = ttsEnabled ? '🔊' : '🔇'; }
  function speak(text) {
    if (!ttsEnabled || !window.speechSynthesis) return;
    const u = new SpeechSynthesisUtterance(text);
    u.lang = currentLang;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
  }

  // ── Textarea auto-resize ──
  textarea.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 160) + 'px';
  });
  textarea.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submitChat(); }
  });

  // ── Scroll ──
  function scrollBottom() { messagesDiv.scrollTop = messagesDiv.scrollHeight; }

  // ── Add bubble ──
  function addBubble(role, text, time) {
    const w = document.getElementById('welcome-screen');
    if (w) w.remove();
    const row = document.createElement('div');
    row.className = 'message-row ' + role;
    row.innerHTML =
      '<div class="avatar ' + role + '-avatar">' + (role === 'user' ? 'D' : '🤖') + '</div>' +
      '<div><div class="bubble">' + escapeHtml(text) + '</div>' +
      '<div class="message-meta">' + time + '</div></div>';
    messagesDiv.appendChild(row);
    scrollBottom();
  }

  function escapeHtml(s) {
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
            .replace(/"/g,'&quot;').replace(/'/g,'&#039;');
  }

  // ── Fill input ──
  function fillInput(text) {
    textarea.value = text;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 160) + 'px';
    textarea.focus();
  }

  // ── Fill and send immediately ──
  function fillAndSend(text) { fillInput(text); submitChat(); }

  // ── Submit chat via AJAX ──
  function submitChat() {
    const cmd = textarea.value.trim();
    if (!cmd) return;
    textarea.value = '';
    textarea.style.height = 'auto';
    sendBtn.disabled = true;
    statusText.textContent = 'Thinking...';

    const now = new Date().toLocaleTimeString('en-US', {hour:'2-digit', minute:'2-digit'});
    addBubble('user', cmd, now);

    fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({command: cmd})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
      addBubble('assistant', d.assistant.text, d.assistant.time);
      speak(d.assistant.text);
      if (d.show_email_modal) openEmailModal();
      statusText.textContent = 'Press Enter to send · Click 🎙️ to speak';
      sendBtn.disabled = false;
      textarea.focus();
    })
    .catch(function() {
      addBubble('assistant', 'Something went wrong. Please try again.', now);
      statusText.textContent = 'Error — try again.';
      sendBtn.disabled = false;
    });
  }

  // ── Clear chat ──
  function clearChat() {
    fetch('/clear', {method: 'POST'})
    .then(function() {
      messagesDiv.innerHTML =
        '<div class="welcome" id="welcome-screen">' +
        '<div class="welcome-icon">🤖</div><h2>How can I help you?</h2>' +
        '<p>Ask me about the weather, set a reminder, search the web, or learn something new.</p>' +
        '<div class="suggestions">' +
        '<div class="suggestion-card" onclick="fillAndSend(\'what is the weather in Addis Ababa\')">' +
        '<div class="suggestion-title">🌤️ Weather</div><div class="suggestion-sub">What\'s the weather in Addis Ababa?</div></div>' +
        '<div class="suggestion-card" onclick="fillAndSend(\'remind me in 5 minutes to drink water\')">' +
        '<div class="suggestion-title">⏰ Reminder</div><div class="suggestion-sub">Remind me in 5 minutes to drink water</div></div>' +
        '<div class="suggestion-card" onclick="fillAndSend(\'who is Albert Einstein\')">' +
        '<div class="suggestion-title">🧠 Knowledge</div><div class="suggestion-sub">Who is Albert Einstein?</div></div>' +
        '<div class="suggestion-card" onclick="fillAndSend(\'search for Python tutorials\')">' +
        '<div class="suggestion-title">🔍 Search</div><div class="suggestion-sub">Search for Python tutorials</div></div>' +
        '</div></div>';
    });
  }

  // ── Email modal ──
  function openEmailModal() { document.getElementById('email-modal').classList.add('open'); }
  function closeEmailModal() { document.getElementById('email-modal').classList.remove('open'); }

  function submitEmail() {
    const email = document.getElementById('user_email').value.trim();
    const pw    = document.getElementById('user_pw').value.trim();
    const errDiv = document.getElementById('email-error');
    const btn   = document.getElementById('email-submit-btn');

    if (!email || !pw) { errDiv.textContent = '❌ Please fill in both fields.'; errDiv.style.display = 'block'; return; }

    btn.textContent = '⏳ Connecting...'; btn.disabled = true;
    errDiv.style.display = 'none';

    fetch('/email-setup', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({email: email, password: pw})
    })
    .then(function(r) { return r.json().then(function(d) { return {ok: r.ok, d: d}; }); })
    .then(function(res) {
      if (!res.ok) {
        errDiv.textContent = res.d.error === 'auth'
          ? '❌ Login failed. Check your email and App Password.'
          : '❌ Could not connect to Gmail. Check your internet.';
        errDiv.style.display = 'block';
        btn.textContent = '🔐 Connect & Read Inbox'; btn.disabled = false;
        return;
      }
      closeEmailModal();
      addBubble('assistant', res.d.assistant.text, res.d.assistant.time);
      speak(res.d.assistant.text);
      btn.textContent = '🔐 Connect & Read Inbox'; btn.disabled = false;
    })
    .catch(function() {
      errDiv.textContent = '❌ Network error. Try again.'; errDiv.style.display = 'block';
      btn.textContent = '🔐 Connect & Read Inbox'; btn.disabled = false;
    });
  }

  // ── Speech recognition ──
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SR) {
    const rec = new SR();
    rec.continuous = false;
    rec.onstart  = function() { micBtn.classList.add('listening'); statusText.textContent = '🎙️ Listening...'; };
    rec.onend    = function() { micBtn.classList.remove('listening'); statusText.textContent = 'Press Enter to send · Click 🎙️ to speak'; };
    rec.onerror  = function(e) { micBtn.classList.remove('listening'); statusText.textContent = 'Mic error: ' + e.error; };
    rec.onresult = function(e) { textarea.value = e.results[0][0].transcript; submitChat(); };
    micBtn.addEventListener('click', function() { rec.lang = currentLang; rec.start(); });
  } else {
    micBtn.disabled = true;
    statusText.textContent = 'Speech not available — use Chrome or Edge.';
  }
</script>

</body>
</html>
"""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template_string(
        HTML,
        history=session.get("history", []),
    )


@app.route("/chat", methods=["POST"])
def chat():
    from datetime import datetime
    from src.email_service import read_inbox

    data = request.get_json(silent=True) or {}
    command = (data.get("command") or "").strip()
    if not command:
        return jsonify({"error": "empty"}), 400

    if "history" not in session:
        session["history"] = []

    now = datetime.now().strftime("%I:%M %p")
    history = session["history"]
    history.append({"role": "user", "text": command, "time": now})

    response = get_response(command)
    show_email_modal = False

    if response == "EMAIL_SETUP_NEEDED":
        if session.get("user_email") and session.get("user_app_password"):
            response = read_inbox(session["user_email"], session["user_app_password"])
            if response in ("EMAIL_AUTH_FAILED", "EMAIL_CONNECT_FAILED"):
                session.pop("user_email", None)
                session.pop("user_app_password", None)
                response = "Your email credentials expired. Please reconnect."
                show_email_modal = True
        else:
            show_email_modal = True
            response = "I need your Gmail credentials to check your inbox."

    history.append({"role": "assistant", "text": response, "time": now})
    session["history"] = history[-40:]
    session.modified = True

    return jsonify({
        "assistant": {"text": response, "time": now},
        "show_email_modal": show_email_modal,
    })


@app.route("/email-setup", methods=["POST"])
def email_setup():
    from datetime import datetime
    from src.email_service import read_inbox

    data = request.get_json(silent=True) or {}
    user_email = (data.get("email") or "").strip()
    user_pw = (data.get("password") or "").strip()

    result = read_inbox(user_email, user_pw)
    if result == "EMAIL_AUTH_FAILED":
        return jsonify({"error": "auth"}), 401
    if result == "EMAIL_CONNECT_FAILED":
        return jsonify({"error": "connect"}), 503

    now = datetime.now().strftime("%I:%M %p")
    session["user_email"] = user_email
    session["user_app_password"] = user_pw
    history = session.get("history", [])
    history.append({"role": "user",      "text": "check my email", "time": now})
    history.append({"role": "assistant", "text": result,           "time": now})
    session["history"] = history[-40:]
    session.modified = True

    return jsonify({"assistant": {"text": result, "time": now}})


@app.route("/clear", methods=["POST"])
def clear():
    session["history"] = []
    session.pop("user_email", None)
    session.pop("user_app_password", None)
    session.modified = True
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
