from flask import Flask, render_template_string, request

from src.assistant import get_response

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Voice Assistant</title>
  <style>
    :root {
      --bg: #f4f7fb;
      --panel: #ffffff;
      --primary: #457b9d;
      --primary-dark: #1d3557;
      --accent: #e63946;
      --muted: #6c7a89;
      --chip: #edf4ff;
      --response-bg: #eaf4ff;
    }
    * { box-sizing: border-box; }
    body {
      font-family: Arial, sans-serif;
      background: linear-gradient(135deg, #eef5ff, var(--bg));
      margin: 0;
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 32px 20px;
    }
    .box {
      width: 100%;
      max-width: 760px;
      background: var(--panel);
      border-radius: 18px;
      box-shadow: 0 18px 40px rgba(29,53,87,0.12);
      padding: 28px;
    }
    h1 {
      margin: 0 0 8px;
      color: var(--primary-dark);
      font-size: 2rem;
    }
    .subtitle {
      margin: 0 0 20px;
      color: var(--muted);
      font-size: 0.98rem;
    }
    .quick-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 16px 0 20px;
    }
    .chip {
      border: 1px solid #d7e5f6;
      background: var(--chip);
      color: var(--primary-dark);
      border-radius: 999px;
      padding: 8px 12px;
      cursor: pointer;
      font-size: 0.9rem;
    }
    input[type="text"] {
      width: 100%;
      padding: 14px 16px;
      font-size: 16px;
      border: 1px solid #ccd5e0;
      border-radius: 10px;
      box-sizing: border-box;
      margin-bottom: 16px;
      outline: none;
    }
    input[type="text"]:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(69, 123, 157, 0.12);
    }
    .controls {
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
    }
    button {
      background: var(--primary);
      color: white;
      border: none;
      border-radius: 10px;
      padding: 12px 20px;
      font-size: 16px;
      cursor: pointer;
      transition: transform 0.15s ease, opacity 0.15s ease;
    }
    button:hover { transform: translateY(-1px); }
    .mic-btn {
      background: var(--accent);
    }
    .status {
      margin-top: 16px;
      font-size: 0.9rem;
      color: var(--muted);
      min-height: 18px;
    }
    .response {
      margin-top: 20px;
      padding: 16px 18px;
      background: var(--response-bg);
      border-left: 5px solid var(--primary);
      border-radius: 10px;
      color: var(--primary-dark);
      min-height: 52px;
      white-space: pre-wrap;
      font-size: 1rem;
    }
  </style>
</head>
<body>
  <div class="box">
    <h1>Voice Assistant</h1>
    <p class="subtitle">Try a command or use the microphone.</p>

    <div class="quick-actions">
      <button type="button" class="chip" data-command="hello">hello</button>
      <button type="button" class="chip" data-command="what time is it">time</button>
      <button type="button" class="chip" data-command="what date is it">date</button>
      <button type="button" class="chip" data-command="what is the weather in Addis Ababa">weather</button>
      <button type="button" class="chip" data-command="search for Python tutorials">search</button>
      <button type="button" class="chip" data-command="remind me in 1 minutes to drink water">reminder</button>
      <button type="button" class="chip" data-command="open my notes">open</button>
    </div>

    <form method="POST" id="assistant-form">
      <input type="text" id="command" name="command" placeholder="Type a command..." value="{{ command or '' }}" required>
      <div class="controls">
        <button type="submit">Send</button>
        <button type="button" class="mic-btn" id="mic-button">🎙️ Speak</button>
      </div>
    </form>

    <div class="status" id="status-text">Assistant ready.</div>

    {% if response %}
      <div class="response" id="response-box">{{ response }}</div>
    {% endif %}
  </div>

  <script>
    const micButton = document.getElementById('mic-button');
    const commandInput = document.getElementById('command');
    const responseBox = document.getElementById('response-box');
    const statusText = document.getElementById('status-text');
    const chips = document.querySelectorAll('.chip');

    chips.forEach(function(chip) {
      chip.addEventListener('click', function() {
        commandInput.value = chip.dataset.command;
        commandInput.focus();
      });
    });

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.lang = 'en-US';
      recognition.continuous = false;

      recognition.onstart = function() {
        statusText.textContent = 'Listening...';
      };

      recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        commandInput.value = transcript;
        statusText.textContent = 'Command captured. Processing...';
        document.getElementById('assistant-form').submit();
      };

      recognition.onerror = function(event) {
        statusText.textContent = 'Mic error: ' + event.error;
        if (responseBox) {
          responseBox.textContent = 'Mic error: ' + event.error;
        }
      };

      micButton.addEventListener('click', function() {
        recognition.start();
      });
    } else {
      micButton.disabled = true;
      micButton.textContent = 'Speech not supported';
      statusText.textContent = 'Browser speech recognition is not available in this browser.';
    }

    function speakResponse(text) {
      if (!('speechSynthesis' in window)) {
        return;
      }
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US';
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(utterance);
    }

    const form = document.getElementById('assistant-form');
    form.addEventListener('submit', function() {
      const text = commandInput.value.trim();
      if (!text) return;
      statusText.textContent = 'Processing request...';
      const currentResponse = responseBox ? responseBox.textContent : '';
      if (currentResponse) {
        speakResponse(currentResponse);
      }
    });
  </script>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    command = ""
    response = ""

    if request.method == "POST":
        command = request.form.get("command", "")
        response = get_response(command)

    return render_template_string(HTML, command=command, response=response)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
