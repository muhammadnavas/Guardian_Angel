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


def extract_final_verdict(full_log: str) -> dict:
    """Parse FINAL_VERDICT block from agent logs."""
    result = {
        "threat_level": "UNKNOWN",
        "threat_score": 0,
        "summary": "",
        "caller_type": "Unknown",
        "recommendation": "",
    }

    verdict_match = re.search(r"FINAL_VERDICT:(.*?)(?:DECISION_DONE|$)", full_log, re.DOTALL | re.IGNORECASE)
    if not verdict_match:
        return result

    block = verdict_match.group(1)

    for key, pattern in [
        ("threat_level", r"Threat Level:\s*(\w+)"),
        ("summary", r"Summary:\s*(.+?)(?:\n-|\Z)"),
        ("caller_type", r"Caller Type:\s*(.+?)(?:\n-|\Z)"),
        ("recommendation", r"Recommendation:\s*(.+?)(?:\n-|\Z|DECISION_DONE)"),
    ]:
        m = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
        if m:
            result[key] = m.group(1).strip()

    score_m = re.search(r"Threat Score:\s*(\d+)", block, re.IGNORECASE)
    if score_m:
        result["threat_score"] = int(score_m.group(1))

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
        for name, (c, i) in agent_styles.items():
            if name in msg:
                color, icon = c, i
                agent_name = name.replace("_", " ")
                break

        # Strip "GUARDIAN_ANGEL_COMPLETE" etc from display
        display_msg = re.sub(r"(GUARDIAN_ANGEL_COMPLETE|SPEECH_DONE|REASONING_DONE|DECISION_DONE)", "", msg).strip()
        if not display_msg:
            continue

        html_parts.append(
            f"<div style='margin-bottom:12px;padding:10px 14px;border-left:3px solid {color};"
            f"background:{color}08;border-radius:0 8px 8px 0'>"
            f"<div style='color:{color};font-size:0.8rem;font-weight:700;margin-bottom:4px'>{icon} {agent_name}</div>"
            f"<div style='font-size:0.88rem;color:#d1d5db;white-space:pre-wrap;line-height:1.5'>{display_msg[:600]}</div>"
            f"</div>"
        )

    return "".join(html_parts) if html_parts else "<div style='color:#6b7280;padding:20px;text-align:center'>⏳ Waiting for agents...</div>"


# ---------------------------------------------------------------------------
# Core analysis function
# ---------------------------------------------------------------------------

async def analyze_call(audio_file, transcript_text, progress=gr.Progress()):
    """Main analysis function called by Gradio."""

    if not audio_file and not transcript_text.strip():
        yield (
            "<div style='text-align:center;padding:30px;color:#ef4444;font-size:1.1rem'>❌ Please upload an audio file or paste a transcript.</div>",
            "<div style='color:#6b7280;padding:20px;text-align:center'>No input provided.</div>",
            "",
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

    progress(0.1, desc="🎙️ Speech Agent: transcribing audio...")

    try:
        if audio_file:
            stream = await team.analyze(audio_path=audio_file)
        else:
            stream = await team.analyze(transcript=transcript_text.strip())

        from autogen_agentchat.base import Response, TaskResult
        from autogen_agentchat.messages import AgentMessage

        agent_progress = {
            "Speech_Agent": 0.25,
            "Reasoning_Agent": 0.50,
            "Decision_Agent": 0.75,
            "Action_Agent": 0.95,
        }

        async for event in stream:
            source = ""
            content_str = ""

            if isinstance(event, TaskResult):
                # Final summary event — iterate its messages
                for m in event.messages:
                    s = getattr(m, "source", "")
                    c = getattr(m, "content", "")
                    if c and isinstance(c, str) and f"[{s}]" not in full_log[-200:]:
                        label = f"[{s}] {c}"
                        messages.append(label)
                        full_log += label + "\n"
                continue
            elif isinstance(event, Response):
                msg = event.chat_message
                source = getattr(msg, "source", "")
                c = getattr(msg, "content", "")
                content_str = c if isinstance(c, str) else ""
            elif hasattr(event, 'source') and hasattr(event, 'content'):
                # Handle AgentMessage and similar objects with source/content attributes
                source = getattr(event, "source", "")
                c = getattr(event, "content", "")
                content_str = c if isinstance(c, str) else ""

            if content_str and source:
                label = f"[{source}] {content_str}"
                messages.append(label)
                full_log += label + "\n"
                p = agent_progress.get(source, 0.9)
                progress(p, desc=f"⚙️ {source.replace('_', ' ')} working...")
                yield (
                    "<div style='text-align:center;padding:30px;color:#f59e0b;font-size:1.1rem'>⏳ Analyzing... please wait.</div>",
                    format_pipeline_log(messages),
                    "",
                )

        progress(1.0, desc="✅ Analysis complete!")
        verdict = extract_final_verdict(full_log)
        result_html = build_result_html(verdict, full_log)

        yield (result_html, format_pipeline_log(messages), full_log)

    except Exception as e:
        import traceback
        err = traceback.format_exc()
        print(err)
        yield (
            f"<div style='color:#ef4444;padding:20px'>❌ Error during analysis:<br><code>{str(e)}</code></div>",
            format_pipeline_log(messages),
            full_log,
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
    max-width: 1100px !important;
    margin: 0 auto !important;
    font-family: 'Segoe UI', Arial, sans-serif !important;
}

.title-banner {
    text-align: center;
    padding: 28px 20px 18px;
    background: linear-gradient(135deg, #1e1b4b 0%, #0a0e1a 100%);
    border-radius: 16px;
    margin-bottom: 20px;
    border: 1px solid #4f46e530;
}

.title-text {
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #818cf8, #f59e0b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
}

.subtitle-text {
    font-size: 1.05rem;
    color: #9ca3af;
    margin-top: 6px;
}

.agent-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    margin: 4px;
}

#analyze-btn {
    background: linear-gradient(135deg, #4f46e5, #6366f1) !important;
    color: white !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    padding: 14px !important;
    border: none !important;
    cursor: pointer !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.35) !important;
    transition: all 0.2s ease !important;
}

#analyze-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45) !important;
}

footer { display: none !important; }
"""

BANNER_HTML = """
<div class="title-banner">
  <div class="title-text">🛡️ Guardian Angel</div>
  <div class="subtitle-text">Autonomous AI Protection for Senior Citizens Against Phone Scams</div>
  <div style="margin-top:14px;display:flex;justify-content:center;gap:8px;flex-wrap:wrap">
    <span class="agent-badge" style="background:#3b82f622;color:#93c5fd;border:1px solid #3b82f640">🎙️ Speech Agent</span>
    <span style="color:#4b5563;font-size:1.2rem;align-self:center">→</span>
    <span class="agent-badge" style="background:#8b5cf622;color:#c4b5fd;border:1px solid #8b5cf640">🧠 Reasoning Agent</span>
    <span style="color:#4b5563;font-size:1.2rem;align-self:center">→</span>
    <span class="agent-badge" style="background:#f59e0b22;color:#fcd34d;border:1px solid #f59e0b40">⚖️ Decision Agent</span>
    <span style="color:#4b5563;font-size:1.2rem;align-self:center">→</span>
    <span class="agent-badge" style="background:#10b98122;color:#6ee7b7;border:1px solid #10b98140">📡 Action Agent</span>
  </div>
</div>
"""

with gr.Blocks(title="Guardian Angel -- Scam Call Detector") as demo:

    gr.HTML(BANNER_HTML)

    with gr.Row():
        # ---- Left column: Input ----
        with gr.Column(scale=1):
            gr.Markdown("### 📥 Input")

            audio_input = gr.Audio(
                label="Upload Call Recording",
                type="filepath",
                sources=["upload"],
                elem_id="audio-upload",
            )

            gr.Markdown("**— OR —**", elem_id="or-divider")

            transcript_input = gr.Textbox(
                label="Paste Call Transcript (for quick demo)",
                placeholder="Type or paste the conversation here...",
                lines=7,
                max_lines=20,
            )

            # Sample transcript buttons — 3 rows of 2
            gr.Markdown("#### Quick Demo Transcripts")
            sample_keys = list(SAMPLE_TRANSCRIPTS.keys())
            for row_start in range(0, len(sample_keys), 2):
                with gr.Row():
                    for label in sample_keys[row_start:row_start + 2]:
                        btn = gr.Button(label, size="sm", variant="secondary")
                        btn.click(
                            fn=lambda l=label: SAMPLE_TRANSCRIPTS[l],
                            outputs=transcript_input,
                        )

            # Real audio file buttons from TrainingData
            if TRAINING_AUDIO_FILES:
                gr.Markdown("#### Real Training Audio Files")
                for audio_path in TRAINING_AUDIO_FILES:
                    fname = os.path.basename(audio_path)
                    audio_btn = gr.Button(fname, size="sm", variant="secondary")
                    audio_btn.click(
                        fn=lambda p=audio_path: p,
                        outputs=audio_input,
                    )

            analyze_btn = gr.Button(
                "Analyze Call",
                variant="primary",
                size="lg",
                elem_id="analyze-btn",
            )


        # ---- Right column: Output ----
        with gr.Column(scale=1):
            gr.Markdown("### 🧠 Agent Pipeline")
            pipeline_output = gr.HTML(
                value="<div style='color:#6b7280;padding:40px;text-align:center;font-size:1.05rem'>"
                      "🛡️ Upload audio or paste a transcript and click <strong>Analyze Call</strong>.</div>"
            )

    gr.Markdown("---")
    gr.Markdown("### 🎯 Analysis Result")
    result_output = gr.HTML(
        value="<div style='color:#6b7280;padding:30px;text-align:center;font-size:1.05rem'>"
              "Results will appear here after analysis.</div>"
    )

    with gr.Accordion("📄 Full Agent Log (Raw)", open=False):
        raw_log = gr.Textbox(label="Raw Log", lines=15, interactive=False)

    # Wire up the analyze button
    analyze_btn.click(
        fn=analyze_call,
        inputs=[audio_input, transcript_input],
        outputs=[result_output, pipeline_output, raw_log],
        show_progress="full",
    )

    gr.Markdown(
        "<div style='text-align:center;color:#6b7280;font-size:0.85rem;margin-top:20px'>"
        "🔒 Guardian Angel — Protecting Senior Citizens from Digital Arrest & Phone Scams | Hackathon 2026"
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
