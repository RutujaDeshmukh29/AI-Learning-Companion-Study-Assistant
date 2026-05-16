"""
Voice Assistant Module
=======================
WHY browser-based Web Speech API (not a paid TTS service):
- Zero cost, zero API keys, works in any modern browser.
- The Web Speech API (SpeechRecognition + SpeechSynthesis) is built into
  Chrome, Edge, and Safari — no library installs needed.
- We inject a small JavaScript component via st.components.v1.html()
  that handles mic input and plays AI responses aloud.

Architecture:
  1. VoiceInput component  — captures speech via JS SpeechRecognition API
                             sends transcript to Streamlit via URL params
  2. VoiceOutput function  — generates JS to speak text via SpeechSynthesis
                             injected after each AI response

Limitations:
  - Requires HTTPS in production (Streamlit Cloud uses HTTPS ✅)
  - Chrome/Edge have best speech recognition support
  - Firefox has limited support (TTS works, STT may not)
"""

from typing import Optional


# ────────────────────────────────────────────────────────────────────────────
# VOICE INPUT — speech-to-text component
# ────────────────────────────────────────────────────────────────────────────
def get_voice_input_html(placeholder: str = "Speak your question...") -> str:
    """
    Return HTML+JS for a voice input button.
    When the user clicks and speaks, the transcript is displayed in a textarea.
    The Streamlit app reads the transcript from a hidden element.

    Use with: st.components.v1.html(get_voice_input_html(), height=120)
    Then read the transcript via JavaScript postMessage to Streamlit.
    """
    return f"""
<html>
<head>
<style>
  body {{
    background: transparent;
    font-family: 'DM Sans', sans-serif;
    margin: 0;
    padding: 8px 0;
  }}
  .voice-container {{
    display: flex;
    align-items: center;
    gap: 12px;
    background: #181c27;
    border: 1px solid #2e3447;
    border-radius: 12px;
    padding: 12px 16px;
  }}
  .mic-btn {{
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: #6c63ff;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    flex-shrink: 0;
    transition: all 0.2s;
  }}
  .mic-btn.listening {{
    background: #ff6b6b;
    animation: pulse 1s infinite;
  }}
  .mic-btn:hover {{ opacity: 0.85; }}
  @keyframes pulse {{
    0%, 100% {{ transform: scale(1); }}
    50% {{ transform: scale(1.1); }}
  }}
  #transcript {{
    flex: 1;
    background: transparent;
    border: none;
    color: #e8eaf0;
    font-size: 0.9rem;
    outline: none;
    resize: none;
    font-family: inherit;
    min-height: 44px;
    max-height: 80px;
  }}
  #status {{
    font-size: 0.75rem;
    color: #7c8499;
    margin-top: 4px;
  }}
</style>
</head>
<body>
<div class="voice-container">
  <button class="mic-btn" id="micBtn" onclick="toggleListening()" title="Click to speak">🎤</button>
  <div style="flex:1">
    <textarea id="transcript" placeholder="{placeholder}" rows="2" readonly></textarea>
    <div id="status">Click the mic to speak</div>
  </div>
</div>

<script>
let recognition = null;
let isListening = false;

function initRecognition() {{
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {{
    document.getElementById('status').textContent = '⚠️ Speech recognition not supported in this browser. Try Chrome.';
    document.getElementById('micBtn').disabled = true;
    return null;
  }}
  const r = new SpeechRecognition();
  r.continuous     = false;
  r.interimResults = true;
  r.lang           = 'en-US';

  r.onstart = () => {{
    isListening = true;
    document.getElementById('micBtn').classList.add('listening');
    document.getElementById('micBtn').textContent = '⏹';
    document.getElementById('status').textContent = '🔴 Listening... speak now';
  }};

  r.onresult = (event) => {{
    const transcript = Array.from(event.results)
      .map(r => r[0].transcript).join('');
    document.getElementById('transcript').value = transcript;

    if (event.results[event.results.length - 1].isFinal) {{
      // Send to Streamlit via postMessage
      window.parent.postMessage({{
        type: 'voice_transcript',
        transcript: transcript
      }}, '*');
    }}
  }};

  r.onend = () => {{
    isListening = false;
    document.getElementById('micBtn').classList.remove('listening');
    document.getElementById('micBtn').textContent = '🎤';
    document.getElementById('status').textContent = '✅ Done — transcript sent';
  }};

  r.onerror = (event) => {{
    isListening = false;
    document.getElementById('micBtn').classList.remove('listening');
    document.getElementById('micBtn').textContent = '🎤';
    document.getElementById('status').textContent = '❌ Error: ' + event.error;
  }};
  return r;
}}

function toggleListening() {{
  if (!recognition) recognition = initRecognition();
  if (!recognition) return;

  if (isListening) {{
    recognition.stop();
  }} else {{
    document.getElementById('transcript').value = '';
    recognition.start();
  }}
}}
</script>
</body>
</html>
"""


# ────────────────────────────────────────────────────────────────────────────
# VOICE OUTPUT — text-to-speech
# ────────────────────────────────────────────────────────────────────────────
def get_tts_html(text: str, auto_play: bool = True, rate: float = 1.0, pitch: float = 1.0) -> str:
    """
    Return an HTML snippet that speaks `text` using the browser's SpeechSynthesis API.
    Use with: st.components.v1.html(get_tts_html(answer), height=60)

    Args:
        text:      The text to read aloud.
        auto_play: Whether to start speaking immediately on load.
        rate:      Speech rate (0.5 = slow, 1.0 = normal, 2.0 = fast).
        pitch:     Voice pitch (0 = low, 1 = normal, 2 = high).
    """
    # Clean text for TTS (remove markdown, emojis, code blocks)
    import re
    clean = re.sub(r'```[\s\S]*?```', 'code block', text)
    clean = re.sub(r'[#*`_\[\]()]', '', clean)
    clean = re.sub(r'https?://\S+', 'link', clean)
    clean = clean[:1500]   # cap length to avoid very long TTS sessions
    # Escape for JS string
    clean = clean.replace("'", "\\'").replace("\n", " ")

    auto_js = "speakText();" if auto_play else ""

    return f"""
<html>
<head>
<style>
  body {{ background:transparent; margin:0; padding:4px 0; font-family:'DM Sans',sans-serif; }}
  .tts-bar {{
    display: flex; align-items: center; gap: 10px;
    background: #1e2333; border: 1px solid #2e3447; border-radius: 8px;
    padding: 6px 12px;
  }}
  button {{
    background: #252a3a; border: 1px solid #2e3447; border-radius: 6px;
    color: #e8eaf0; cursor: pointer; padding: 4px 10px; font-size: 0.8rem;
    transition: all 0.2s;
  }}
  button:hover {{ background: #6c63ff; border-color: #6c63ff; }}
  #tts-status {{ font-size: 0.75rem; color: #7c8499; }}
</style>
</head>
<body>
<div class="tts-bar">
  <span style="font-size:1rem;">🔊</span>
  <button onclick="speakText()">▶ Play</button>
  <button onclick="window.speechSynthesis.pause()">⏸ Pause</button>
  <button onclick="window.speechSynthesis.cancel()">⏹ Stop</button>
  <span id="tts-status">AI Voice Ready</span>
</div>
<script>
function speakText() {{
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance('{clean}');
  utterance.rate  = {rate};
  utterance.pitch = {pitch};
  utterance.lang  = 'en-US';

  // Prefer a natural-sounding voice
  const voices = window.speechSynthesis.getVoices();
  const preferred = voices.find(v =>
    v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Neural')
  );
  if (preferred) utterance.voice = preferred;

  utterance.onstart = () => {{
    document.getElementById('tts-status').textContent = '🔊 Speaking...';
  }};
  utterance.onend = () => {{
    document.getElementById('tts-status').textContent = '✅ Done';
  }};
  utterance.onerror = (e) => {{
    document.getElementById('tts-status').textContent = '❌ ' + e.error;
  }};
  window.speechSynthesis.speak(utterance);
}}

// Some browsers need a tiny delay to load voices
window.speechSynthesis.onvoiceschanged = () => {{ {auto_js} }};
setTimeout(() => {{ {auto_js} }}, 300);
</script>
</body>
</html>
"""