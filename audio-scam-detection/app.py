"""
Guardian Angel — Gradio UI for Audio Call Scam Detection
Senior-friendly interface with 4-agent agentic pipeline visualization.
"""

import asyncio
import os
import re
import gradio as gr

from agents_audio import GuardianAngelTeam
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

# ---------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------

_team: GuardianAngelTeam | None = None

def get_team() -> GuardianAngelTeam:
    global _team
    if _team is None:
        print("🔄 Initializing Guardian Angel Team...")
        _team = GuardianAngelTeam()
        print("✅ Guardian Angel Team ready")
    return _team


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

THREAT_COLORS = {
    "SAFE": "#10b981",
    "SUSPICIOUS": "#f59e0b",
    "HIGH_RISK": "#ef4444",
    "CRITICAL": "#dc2626",
}

THREAT_EMOJIS = {
    "SAFE": "✅",
    "SUSPICIOUS": "⚠️",
    "HIGH_RISK": "🔴",
    "CRITICAL": "🚨",
}


def _strip_md(text: str) -> str:
    """Strip markdown bold/italic/code from a string."""
    return re.sub(r"[*_`#]+", "", text).strip()


def extract_final_verdict(full_log: str) -> dict:
    """Parse FINAL_VERDICT block from agent logs.
    Robust against markdown formatting and varied LLM output styles.
    """
    result = {
        "threat_level": "UNKNOWN",
        "threat_score": 0,
        "summary": "",
        "caller_type": "Unknown",
        "recommendation": "",
    }

    # Try to find FINAL_VERDICT block first
    verdict_match = re.search(r"FINAL_VERDICT[:\s]*(.*?)(?:DECISION_DONE|$)", full_log, re.DOTALL | re.IGNORECASE)
    block = verdict_match.group(1) if verdict_match else full_log  # fall back to full log

    # Threat level — allow markdown bold, underscores, slashes, mixed case
    tl_m = re.search(
        r"Threat\s*Level[:\s*_]+(SAFE|SUSPICIOUS|HIGH[_\s]RISK|CRITICAL)",
        block, re.IGNORECASE
    )
    if tl_m:
        result["threat_level"] = _strip_md(tl_m.group(1)).upper().replace(" ", "_")
    else:
        # Fallback: scan for the level keyword anywhere
        for lvl in ("CRITICAL", "HIGH_RISK", "HIGH RISK", "SUSPICIOUS", "SAFE"):
            if lvl.lower() in block.lower():
                result["threat_level"] = lvl.replace(" ", "_")
                break

    # Threat score — e.g.  "Threat Score: **95**" or "score: 95/100"
    score_m = re.search(r"Threat\s*Score[:\s*_]+(\d+)", block, re.IGNORECASE)
    if not score_m:
        score_m = re.search(r"score[:\s]+(\d+)\s*(?:/\s*100)?", block, re.IGNORECASE)
    if score_m:
        result["threat_score"] = int(score_m.group(1))

    # Summary, Caller Type, Recommendation — stop at next bullet, next field, or end
    stop = r"(?=\n\s*[-*]\s+\w|DECISION_DONE|$)"
    for key, label in [
        ("summary",        r"Summary"),
        ("caller_type",    r"Caller\s*Type"),
        ("recommendation", r"Recommendation"),
    ]:
        m = re.search(rf"{label}[:\s*_]+(.+?){stop}", block, re.DOTALL | re.IGNORECASE)
        if m:
            result[key] = _strip_md(m.group(1)).strip()

    return result


def build_result_html(verdict: dict, actions_log: str) -> str:
    """Render a rich HTML result card."""
    level = verdict.get("threat_level", "UNKNOWN")
    score = verdict.get("threat_score", 0)
    summary = verdict.get("summary", "No summary available.")
    caller_type = verdict.get("caller_type", "Unknown")
    recommendation = verdict.get("recommendation", "")
    color = THREAT_COLORS.get(level, "#6b7280")
    emoji = THREAT_EMOJIS.get(level, "❓")

    bar_pct = score
    bar_color = color

    # Keyword chips from actions_log
    def extract_list(label: str) -> list[str]:
        m = re.search(rf'"{label}":\s*\[(.*?)\]', actions_log, re.DOTALL)
        if not m:
            return []
        raw = m.group(1)
        return [s.strip(' "\'') for s in raw.split(",") if s.strip(' "\'')]

    fear = extract_list("fear_indicators")
    authority = extract_list("authority_indicators")
    urgency = extract_list("urgency_indicators")
    financial = extract_list("financial_indicators")

    def chips(items: list[str], chip_color: str) -> str:
        if not items:
            return "<span style='color:#6b7280;font-size:0.9em'>None detected</span>"
        return " ".join(
            f"<span style='background:{chip_color}22;color:{chip_color};border:1px solid {chip_color}55;"
            f"padding:2px 10px;border-radius:999px;font-size:0.82em;margin:2px;display:inline-block'>{i}</span>"
            for i in items
        )

    # Alert actions
    alert_html = ""
    if "Family notified" in actions_log or "family" in actions_log.lower():
        alert_html += "<span style='color:#f59e0b'>📱 Family notified (simulated)</span><br>"
    if "Police" in actions_log or "police" in actions_log.lower():
        alert_html += "<span style='color:#ef4444'>🚓 Cybercrime police alerted (simulated)</span><br>"
    if not alert_html:
        alert_html = "<span style='color:#10b981'>ℹ️ No external alerts required</span>"

    return f"""
<div style="font-family:'Segoe UI',Arial,sans-serif;max-width:720px;margin:0 auto;">

  <!-- Verdict Banner -->
  <div style="background:linear-gradient(135deg,{color}22,{color}08);border:2px solid {color}66;
              border-radius:16px;padding:28px;text-align:center;margin-bottom:18px;">
    <div style="font-size:3.5rem;margin-bottom:8px">{emoji}</div>
    <div style="font-size:2rem;font-weight:800;color:{color};letter-spacing:-0.5px">{level.replace('_',' ')}</div>
    <div style="color:#9ca3af;margin-top:4px;font-size:0.95rem">Caller Type: <strong style="color:#f9fafb">{caller_type}</strong></div>
  </div>

  <!-- Score bar -->
  <div style="background:#1f2937;border-radius:12px;padding:18px 22px;margin-bottom:14px;">
    <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:0.9rem;color:#9ca3af">
      <span>Threat Score</span><span style="color:{color};font-weight:700">{score}/100</span>
    </div>
    <div style="background:#374151;border-radius:999px;height:10px;overflow:hidden">
      <div style="width:{bar_pct}%;height:100%;background:{bar_color};border-radius:999px;
                  transition:width 1s ease;box-shadow:0 0 8px {bar_color}88"></div>
    </div>
  </div>

  <!-- Summary -->
  <div style="background:#1f2937;border-radius:12px;padding:18px 22px;margin-bottom:14px;">
    <div style="color:#9ca3af;font-size:0.85rem;font-weight:600;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.05em">📋 Analysis Summary</div>
    <div style="font-size:1.05rem;line-height:1.6;color:#f9fafb">{summary}</div>
  </div>

  <!-- Recommendation -->
  {"" if not recommendation else f'''
  <div style="background:#fef3c7;border:1px solid #fbbf24;border-radius:12px;padding:16px 20px;margin-bottom:14px;">
    <div style="color:#92400e;font-size:0.85rem;font-weight:700;margin-bottom:6px;text-transform:uppercase">⚡ What To Do Now</div>
    <div style="color:#78350f;font-size:1rem;line-height:1.5">{recommendation}</div>
  </div>'''}

  <!-- Keyword Indicators -->
  <div style="background:#1f2937;border-radius:12px;padding:18px 22px;margin-bottom:14px;">
    <div style="color:#9ca3af;font-size:0.85rem;font-weight:600;margin-bottom:12px;text-transform:uppercase;letter-spacing:0.05em">🔍 Detected Indicators</div>
    <table style="width:100%;font-size:0.88rem;border-collapse:separate;border-spacing:0 6px">
      <tr>
        <td style="color:#6b7280;padding-right:12px;width:130px;vertical-align:top">😰 Fear</td>
        <td>{chips(fear, "#ef4444")}</td>
      </tr>
      <tr>
        <td style="color:#6b7280;padding-right:12px;vertical-align:top">🏛️ Authority</td>
        <td>{chips(authority, "#f59e0b")}</td>
      </tr>
      <tr>
        <td style="color:#6b7280;padding-right:12px;vertical-align:top">⏰ Urgency</td>
        <td>{chips(urgency, "#8b5cf6")}</td>
      </tr>
      <tr>
        <td style="color:#6b7280;padding-right:12px;vertical-align:top">💸 Financial</td>
        <td>{chips(financial, "#06b6d4")}</td>
      </tr>
    </table>
  </div>

  <!-- Alert Actions -->
  <div style="background:#1f2937;border-radius:12px;padding:16px 22px;">
    <div style="color:#9ca3af;font-size:0.85rem;font-weight:600;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.05em">🔔 Alert Actions Taken</div>
    <div style="font-size:0.95rem;line-height:1.8">{alert_html}</div>
  </div>

</div>
"""


def format_pipeline_log(messages: list[str]) -> str:
    """Format streaming agent log messages into readable HTML."""
    agent_styles = {
        "Speech_Agent":    ("#3b82f6", "🎙️"),
        "Reasoning_Agent": ("#8b5cf6", "🧠"),
        "Decision_Agent":  ("#f59e0b", "⚖️"),
        "Action_Agent":    ("#10b981", "📡"),
    }

    html_parts = []
    for msg in messages:
        color, icon = "#6b7280", "💬"
        agent_name = "System"
        
        # Detect agent from message
        for name, (c, i) in agent_styles.items():
            if name in msg:
                color, icon = c, i
                agent_name = name.replace("_", " ")
                break

        # Clean up the message - remove technical prefixes and agent names
        display_msg = msg
        
        # Remove agent name prefix like "[Speech_Agent]"
        display_msg = re.sub(r"^\[.*?\]\s*", "", display_msg)
        
        # Remove technical keywords
        cleanup_patterns = [
            r"GUARDIAN_ANGEL_COMPLETE|SPEECH_DONE|REASONING_DONE|DECISION_DONE",
            r"TRANSCRIPT_PROVIDED:\s*",
            r"ANALYSIS_COMPLETE:\s*",
            r"THREAT_ASSESSMENT:\s*",
            r"FINAL_VERDICT:\s*",
        ]
        
        for pattern in cleanup_patterns:
            display_msg = re.sub(pattern, "", display_msg, flags=re.IGNORECASE)
        
        display_msg = display_msg.strip()
        
        # Skip empty messages
        if not display_msg:
            continue
            
        # Format based on agent type
        if "Speech_Agent" in msg:
            if "IMAGE FILE PATH" in msg or "extract_image_text" in display_msg.lower() or "ocr" in display_msg.lower():
                display_msg = f"🖼️ Extracting text from screenshot...\n{display_msg[:400]}{'...' if len(display_msg) > 400 else ''}"
            elif any(kw in display_msg for kw in ["Good afternoon", "Hello", "TRANSCRIPT_PROVIDED"]):
                display_msg = f"📝 Text extracted:\n\n\"{display_msg[:300]}{'...' if len(display_msg) > 300 else ''}\""
            else:
                display_msg = f"🎙️ {display_msg}"
        elif "Reasoning_Agent" in msg:
            display_msg = f"🧠 Analyzing potential scam indicators...\n{display_msg[:400]}{'...' if len(display_msg) > 400 else ''}"
        elif "Decision_Agent" in msg:
            display_msg = f"⚖️ Making threat assessment...\n{display_msg[:400]}{'...' if len(display_msg) > 400 else ''}"
        elif "Action_Agent" in msg:
            display_msg = f"📡 Taking protective actions...\n{display_msg[:400]}{'...' if len(display_msg) > 400 else ''}"

        html_parts.append(
            f"<div style='margin-bottom:12px;padding:12px 16px;border-left:4px solid {color};"
            f"background:{color}12;border-radius:0 8px 8px 0'>"
            f"<div style='color:{color};font-size:0.85rem;font-weight:700;margin-bottom:6px'>{icon} {agent_name}</div>"
            f"<div style='font-size:0.9rem;color:#1f2937;white-space:pre-wrap;line-height:1.5'>{display_msg}</div>"
            f"</div>"
        )

    return "".join(html_parts) if html_parts else "<div style='color:#374151;padding:20px;text-align:center'>⏳ Waiting for agents...</div>"


# ---------------------------------------------------------------------------
# Core analysis function
# ---------------------------------------------------------------------------

async def analyze_call(audio_file, image_file, transcript_text, progress=gr.Progress()):
    """Main analysis function called by Gradio."""

    if not audio_file and not image_file and not transcript_text.strip():
        yield (
            "<div style='text-align:center;padding:30px;color:#ef4444;font-size:1.1rem'>❌ Please upload an audio file, a screenshot, or paste a transcript.</div>",
            "<div style='color:#6b7280;padding:20px;text-align:center'>No input provided.</div>",
        )
        return

    team = get_team()
    try:
        await team.reset()
    except RuntimeError as e:
        # Team hasn't been run yet, so reset is not needed
        if "not been initialized" not in str(e):
            raise

    progress(0.05, desc="🔄 Starting Guardian Angel pipeline...")

    messages = []
    full_log = ""

    if image_file:
        progress(0.1, desc="🖼️ Speech Agent: extracting text from screenshot...")
    elif audio_file:
        progress(0.1, desc="🎙️ Speech Agent: transcribing audio...")
    else:
        progress(0.1, desc="📝 Processing transcript...")

    try:
        if audio_file:
            stream = await team.analyze(audio_path=audio_file)
        elif image_file:
            stream = await team.analyze(image_path=image_file)
        else:
            stream = await team.analyze(transcript=transcript_text.strip())

        from autogen_agentchat.base import Response, TaskResult
        from autogen_agentchat.messages import TextMessage, ToolCallMessage, ToolCallResultMessage

        KNOWN_AGENTS = {"Speech_Agent", "Reasoning_Agent", "Decision_Agent", "Action_Agent"}

        agent_progress = {
            "Speech_Agent": 0.25,
            "Reasoning_Agent": 0.50,
            "Decision_Agent": 0.75,
            "Action_Agent": 0.95,
        }

        # Track which agents have live-streamed entries (keyed by source → messages index)
        agent_msg_index: dict[str, int] = {}

        async for event in stream:

            if isinstance(event, TaskResult):
                # TaskResult is the authoritative final record — rebuild full_log from it
                # so FINAL_VERDICT is always captured regardless of streaming order
                final_messages: list[str] = []
                final_log = ""
                for m in event.messages:
                    s = getattr(m, "source", "")
                    if s not in KNOWN_AGENTS:
                        continue
                    c = getattr(m, "content", "")
                    if not c or not isinstance(c, str):
                        continue
                    label = f"[{s}] {c}"
                    # Keep only the LAST message per agent (final text after tool results)
                    final_messages = [x for x in final_messages if not x.startswith(f"[{s}]")]
                    final_messages.append(label)
                    final_log = "\n".join(final_messages) + "\n"

                # Merge: prefer TaskResult content but keep display order stable
                if final_log:
                    messages = final_messages
                    full_log = final_log
                    print("=== FULL_LOG FROM TaskResult ===")
                    print(full_log[:3000])
                continue

            # Live streaming: capture TextMessage events from known agents for real-time display
            if isinstance(event, TextMessage):
                source = getattr(event, "source", "")
                content_str = getattr(event, "content", "")
            elif isinstance(event, Response):
                msg = event.chat_message
                source = getattr(msg, "source", "")
                content_str = getattr(msg, "content", "") if isinstance(getattr(msg, "content", ""), str) else ""
            else:
                continue

            if source not in KNOWN_AGENTS or not content_str:
                continue

            p = agent_progress.get(source, 0.9)
            progress(p, desc=f"⚙️ {source.replace('_', ' ')} working...")

            if source not in agent_msg_index:
                # First message from this agent — append
                agent_msg_index[source] = len(messages)
                messages.append(f"[{source}] {content_str}")
                full_log += f"[{source}] {content_str}\n"
            else:
                # Follow-up message (after tool results) — update in place
                idx = agent_msg_index[source]
                messages[idx] = f"[{source}] {content_str}"
                # Rebuild full_log from current messages list
                full_log = "\n".join(messages) + "\n"

            yield (
                "<div style='text-align:center;padding:30px;color:#f59e0b;font-size:1.1rem'>⏳ Analyzing... please wait.</div>",
                format_pipeline_log(messages),
            )

        progress(1.0, desc="✅ Analysis complete!")

        if not messages:
            # No agent output at all — likely a rate limit or API error
            pipeline_html = (
                "<div style='padding:20px;border-left:4px solid #ef4444;background:#ef444412;"
                "border-radius:0 8px 8px 0;color:#ef4444;font-size:0.95rem;line-height:1.6'>"
                "<strong>⚠️ No agent responses received.</strong><br>"
                "This is usually caused by an API rate limit or quota exceeded error.<br>"
                "Please wait a moment and try again, or check the server terminal for details."
                "</div>"
            )
            result_html = (
                "<div style='padding:24px;border:2px solid #ef444440;border-radius:14px;"
                "background:#111827;color:#f87171;font-size:1rem;line-height:1.7'>"
                "❌ <strong>Analysis failed</strong> — No agents responded. "
                "Check the server terminal for the error (likely a rate limit / quota issue)."
                "</div>"
            )
            yield (result_html, pipeline_html)
            return

        verdict = extract_final_verdict(full_log)
        result_html = build_result_html(verdict, full_log)

        yield (result_html, format_pipeline_log(messages))

    except Exception as e:
        import traceback
        err = traceback.format_exc()
        print(err)
        yield (
            f"<div style='color:#ef4444;padding:20px'>❌ Error during analysis:<br><code>{str(e)}</code></div>",
            format_pipeline_log(messages),
        )


# ---------------------------------------------------------------------------
# Sample transcripts for quick demo
# ---------------------------------------------------------------------------

TRAINING_DIR = os.path.join(os.path.dirname(__file__), "TrainingData")

# Text transcript samples (6 total including real TrainingData cases)
SAMPLE_TRANSCRIPTS = {
    "CRITICAL — Digital Arrest (Inspector Rao)": (
        # student_true_positive.txt
        "Hello. This is Inspector Rao from the Cyber Crime Unit. "
        "Your Aadhaar details are linked to a serious digital case, and you are currently under digital arrest. "
        "You must remain on this call and follow instructions, otherwise the matter will be escalated for immediate legal action."
    ),
    "CRITICAL — CBI Drug Trafficking": (
        "Hello, I am Inspector Rajesh Kumar from CBI Cybercrime Division. "
        "Your Aadhaar number has been used in illegal drug trafficking. "
        "A warrant has been issued for your arrest. "
        "You must pay a security deposit of 2 lakh rupees immediately to avoid being detained. "
        "Do not hang up or we will send police to your house. This is your last warning."
    ),
    "HIGH RISK — Sophisticated Compliance Scam": (
        # student_false_negative.txt — a tricky social-engineering scam
        "Good afternoon. This is a verification officer from the Compliance Review Desk "
        "from Customes department regarding a routine internal profile check linked to your identity record. "
        "There is a minor inconsistency that needs to be resolved today to avoid automated system escalation, "
        "so we request that you remain available on this call until the review is completed."
    ),
    "HIGH RISK — Customs Parcel": (
        "This is TRAI Telecom Authority. A parcel in your name has been seized at customs. "
        "Our officer will connect you to the enforcement directorate. "
        "You must pay a fine of 50,000 rupees today to clear your name. "
        "Your bank account will be frozen if you delay."
    ),
    "SUSPICIOUS — Bank OTP Phishing": (
        "Hello sir, I am calling from SBI bank. "
        "Your account shows some unusual activity. "
        "Please share your OTP to verify your identity and avoid account suspension."
    ),
    "SAFE — Doctor Appointment Reminder": (
        "Hello, this is a reminder call from City Hospital. "
        "Your appointment with Dr. Sharma is scheduled for tomorrow at 3 PM. "
        "Please bring your previous reports. Thank you."
    ),
}

# Real TrainingData audio files for upload examples
def _get_training_audio_files():
    """Return list of available audio files from TrainingData folder."""
    audio_exts = {".mp3", ".m4a", ".wav", ".ogg"}
    files = []
    if os.path.isdir(TRAINING_DIR):
        for f in sorted(os.listdir(TRAINING_DIR)):
            if any(f.lower().endswith(ext) for ext in audio_exts):
                files.append(os.path.join(TRAINING_DIR, f))
    return files

TRAINING_AUDIO_FILES = _get_training_audio_files()




# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

CSS = """
.gradio-container {
    max-width: 1400px !important;
    margin: 0 auto !important;
    font-family: 'Segoe UI', Arial, sans-serif !important;
    color: #111827 !important;
}

/* ── All Gradio native text darker ── */
.gradio-container label,
.gradio-container .label-wrap,
.gradio-container span.svelte-1gfkn6j,
.gradio-container .block span,
.gradio-container .block label span,
.gradio-container p,
.gradio-container li,
.gradio-container h1, .gradio-container h2,
.gradio-container h3, .gradio-container h4 {
    color: #111827 !important;
}

/* Fix CSS syntax to ensure body text color is overridden across the theme */
body, .gradio-container, .dark {
    --body-text-color: #111827 !important;
    --body-text-color-subdued: #4b5563 !important;
    --input-text-color: #111827 !important;
    --placeholder-text-color: #6b7280 !important;
    --block-title-text-color: #111827 !important;
}

/* Input / textarea text */
.gradio-container input,
.gradio-container textarea,
.gradio-container [data-testid="textbox"] {
    color: #111827 !important;
    background-color: #ffffff !important;
    opacity: 1 !important;
    font-weight: 500 !important;
}


/* Tab labels */
.gradio-container .tab-nav button {
    color: #374151 !important;
    font-weight: 600 !important;
}
.gradio-container .tab-nav button.selected {
    color: #4f46e5 !important;
}

/* Accordion header */
.gradio-container .accordion-header span {
    color: #111827 !important;
    font-weight: 600 !important;
}

/* Secondary (demo) buttons */
.gradio-container button.secondary {
    color: #1f2937 !important;
    font-weight: 600 !important;
}

.title-banner {
    text-align: center;
    padding: 32px 24px 22px;
    background: linear-gradient(135deg, #1e1b4b 0%, #0a0e1a 100%);
    border-radius: 16px;
    margin-bottom: 24px;
    border: 1px solid #4f46e530;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.title-text {
    font-size: 2.8rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #818cf8, #f59e0b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 8px;
}

.subtitle-text {
    font-size: 1.1rem;
    color: #9ca3af;
    margin-top: 8px;
    line-height: 1.5;
}

.agent-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
    margin: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

#analyze-btn {
    background: linear-gradient(135deg, #4f46e5, #6366f1) !important;
    color: white !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    padding: 16px !important;
    border: none !important;
    cursor: pointer !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
    transition: all 0.3s ease !important;
    margin-top: 16px !important;
}

#analyze-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
}

footer { display: none !important; }
"""

BANNER_HTML = """
<div class="title-banner">
  <div class="title-text">🛡️ Guardian Angel</div>
  <div class="subtitle-text">Autonomous AI Protection for Senior Citizens Against Phone Scams</div>
  <div style="margin-top:16px;display:flex;justify-content:center;align-items:center;gap:10px;flex-wrap:wrap">
    <span class="agent-badge" style="background:#3b82f622;color:#93c5fd;border:1px solid #3b82f640">🎙️ Speech Agent</span>
    <span style="color:#6b7280;font-size:1.4rem">→</span>
    <span class="agent-badge" style="background:#8b5cf622;color:#c4b5fd;border:1px solid #8b5cf640">🧠 Reasoning Agent</span>
    <span style="color:#6b7280;font-size:1.4rem">→</span>
    <span class="agent-badge" style="background:#f59e0b22;color:#fcd34d;border:1px solid #f59e0b40">⚖️ Decision Agent</span>
    <span style="color:#6b7280;font-size:1.4rem">→</span>
    <span class="agent-badge" style="background:#10b98122;color:#6ee7b7;border:1px solid #10b98140">📡 Action Agent</span>
  </div>
</div>
"""

with gr.Blocks(title="Guardian Angel -- Scam Detector") as demo:

    gr.HTML(BANNER_HTML)

    with gr.Tabs():

        # ══════════════════════════════════════════════════
        # TAB 1 — Call Analysis
        # ══════════════════════════════════════════════════
        with gr.TabItem("📞 Call Analysis"):
            with gr.Row():
                # ---- Left: Input ----
                with gr.Column(scale=1):
                    gr.HTML("""
                        <div style='font-size:1.2rem;font-weight:700;color:#111827;margin:8px 0 14px;
                                    padding-bottom:8px;border-bottom:2px solid #d1d5db'>
                            📥 Input
                        </div>
                    """)

                    audio_input = gr.Audio(
                        label="🎙️ Upload Call Recording",
                        type="filepath",
                        sources=["upload"],
                    )

                    gr.HTML("<div style='text-align:center;margin:12px 0;color:#374151;font-weight:700;font-size:0.9rem'>— OR —</div>")

                    transcript_input = gr.Textbox(
                        label="📝 Paste Call Transcript",
                        placeholder="Type or paste the conversation here...",
                        lines=7,
                        max_lines=25,
                    )

                    gr.HTML("""
                        <div style='font-size:1rem;font-weight:600;color:#374151;margin-top:16px;margin-bottom:8px'>
                            📋 Quick Demo Transcripts
                        </div>
                    """)
                    sample_keys = list(SAMPLE_TRANSCRIPTS.keys())
                    for row_start in range(0, len(sample_keys), 2):
                        with gr.Row():
                            for label in sample_keys[row_start:row_start + 2]:
                                btn = gr.Button(label, size="sm", variant="secondary")
                                btn.click(
                                    fn=lambda l=label: SAMPLE_TRANSCRIPTS[l],
                                    outputs=transcript_input,
                                )

                    if TRAINING_AUDIO_FILES:
                        gr.HTML("""
                            <div style='font-size:1rem;font-weight:600;color:#374151;margin-top:16px;margin-bottom:8px'>
                                🎵 Real Training Audio Files
                            </div>
                        """)
                        for audio_path in TRAINING_AUDIO_FILES:
                            fname = os.path.basename(audio_path)
                            audio_btn = gr.Button(fname, size="sm", variant="secondary")
                            audio_btn.click(fn=lambda p=audio_path: p, outputs=audio_input)

                    call_analyze_btn = gr.Button("🔍 Analyze Call", variant="primary", size="lg", elem_id="analyze-btn")

                # ---- Right: Pipeline ----
                with gr.Column(scale=1):
                    gr.HTML("""
                        <div style='font-size:1.2rem;font-weight:700;color:#4f46e5;margin:8px 0 14px;
                                    padding-bottom:8px;border-bottom:2px solid #4f46e540'>
                            🧠 Agent Pipeline
                        </div>
                    """)
                    call_pipeline_output = gr.HTML(
                        value="<div style='color:#374151;padding:40px;text-align:center;font-size:1rem'>"
                              f"🛡️ Upload audio or paste a transcript, then click <strong>Analyze Call</strong>.</div>"
                    )

            call_result_output = gr.HTML(
                value="<div style='color:#374151;padding:30px;text-align:center;font-size:1rem'>"
                      "Results will appear here after analysis.</div>"
            )

            call_analyze_btn.click(
                fn=analyze_call,
                inputs=[audio_input, gr.State(None), transcript_input],
                outputs=[call_result_output, call_pipeline_output],
                show_progress="full",
            )

    gr.HTML(
        "<div style='text-align:center;color:#6b7280;font-size:0.88rem;margin-top:24px;padding:16px'>"
        "🔒 <strong>Guardian Angel</strong> — Protecting Senior Citizens from Digital Arrest & Phone Scams | Hackathon 2026"
        "</div>"
    )

if __name__ == "__main__":
    ga_theme = gr.themes.Base(
        primary_hue="indigo",
        secondary_hue="amber",
        neutral_hue="gray",
        font=gr.themes.GoogleFont("Inter"),
    )
    demo.queue(default_concurrency_limit=3).launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
        show_error=True,
        theme=ga_theme,
        css=CSS,
    )
