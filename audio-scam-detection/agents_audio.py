"""
Guardian Angel — Audio Call Scam Detection Pipeline
4-Agent AutoGen Team:
  1. Speech Agent   → transcribes audio using Whisper
  2. Reasoning Agent → rule-based + LLM scam analysis
  3. Decision Agent  → aggregates score → threat level
  4. Action Agent    → triggers alerts + stores to DB
"""

import os
import json
from typing import Optional

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv, find_dotenv

from tools import SpeechTranscriber, ScamDetector, AlertSystem, DatabaseConnector


load_dotenv(find_dotenv(), override=True)


# ---------------------------------------------------------------------------
# Tool wrappers (plain functions for FunctionTool)
# ---------------------------------------------------------------------------

_transcriber: Optional[SpeechTranscriber] = None
_detector = ScamDetector()
_alert = AlertSystem()
_db = DatabaseConnector()
_ocr = ImageOCR()


def _get_transcriber() -> SpeechTranscriber:
    global _transcriber
    if _transcriber is None:
        _transcriber = SpeechTranscriber(model_size="base")
    return _transcriber


def transcribe_audio(audio_path: str) -> str:
    """Transcribe an audio file to text using OpenAI Whisper.
    Returns the transcript text or an error string.
    """
    return _get_transcriber().transcribe(audio_path)


def extract_image_text(image_path: str) -> str:
    """Extract text from a screenshot or image using OCR.
    Returns the extracted text or an error string.
    """
    return _ocr.extract_text(image_path)


def analyze_transcript(transcript: str) -> str:
    """Analyse a call transcript for scam indicators using rule-based detection.
    Returns a JSON string with threat_score and indicator lists.
    """
    result = _detector.analyze_text(transcript)
    return json.dumps(result, ensure_ascii=False)


def get_threat_level(threat_score: int) -> str:
    """Map numeric threat score (0-100) to a threat level label."""
    return _detector.get_threat_level(threat_score)


def trigger_alert(threat_level: str, summary: str) -> str:
    """Trigger appropriate alerts (family/police) based on threat level.
    Returns a string describing actions taken.
    """
    return _alert.escalate(threat_level, summary)


def store_call_result(
    transcript: str,
    summary: str,
    threat_level: str,
    threat_score: int,
    fear_indicators: list,
    authority_indicators: list,
    urgency_indicators: list,
    financial_indicators: list,
    alert_sent: bool,
    language: str = "unknown",
) -> str:
    """Store the call analysis result in MongoDB. Returns the document ID or 'duplicate'."""
    doc_id = _db.store_result(
        transcript=transcript,
        summary=summary,
        threat_level=threat_level,
        threat_score=threat_score,
        language=language,
        fear_indicators=fear_indicators,
        authority_indicators=authority_indicators,
        urgency_indicators=urgency_indicators,
        financial_indicators=financial_indicators,
        alert_sent=alert_sent,
    )
    return doc_id or "duplicate"


# ---------------------------------------------------------------------------
# Agent team
# ---------------------------------------------------------------------------

class GuardianAngelTeam:
    """
    4-agent AutoGen team for audio call scam detection.
    """

    def __init__(self):
        self.model = self._init_model()
        self.team = self._build_team()

    def _init_model(self) -> OpenAIChatCompletionClient:
        # Try OpenAI first, fallback to Gemini
        openai_key = os.getenv("OPENAI_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")
        
        if openai_key and openai_key != "your_openai_api_key_here":
            print("🔄 Using OpenAI GPT-4o-mini model")
            return OpenAIChatCompletionClient(
                model="gpt-4o-mini",
                api_key=openai_key,
                model_capabilities={
                    "vision": False,
                    "function_calling": True,
                    "json_output": True,
                },
            )
        elif gemini_key:
            print("Using Gemini 2.0 Flash model")
            return OpenAIChatCompletionClient(
                model="gemini-2.5-flash",
                api_key=gemini_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                timeout=30.0,  # 30 second timeout
                max_retries=3,  # Retry on failures
                model_capabilities={
                    "vision": False,
                    "function_calling": True,
                    "json_output": True,
                },
            )
        else:
            raise ValueError("No valid API key found. Please set OPENAI_API_KEY or GEMINI_API_KEY in your .env file")

    def _build_team(self) -> RoundRobinGroupChat:
        # --- Tools ---
        transcribe_tool = FunctionTool(transcribe_audio, description="Transcribes an audio file (.wav/.mp3/.m4a) to text using Whisper. Pass the absolute file path.")
        ocr_tool = FunctionTool(extract_image_text, description="Extracts text from a screenshot or image file (PNG/JPG/JPEG) using OCR. Pass the absolute file path.")
        analyze_tool = FunctionTool(analyze_transcript, description="Analyses a call transcript for fear/authority/urgency/financial scam indicators. Returns JSON with threat_score and indicator lists.")
        threat_level_tool = FunctionTool(get_threat_level, description="Converts a numeric threat_score (0–100) to SAFE, SUSPICIOUS, HIGH_RISK, or CRITICAL.")
        alert_tool = FunctionTool(trigger_alert, description="Sends alerts to family/police based on threat level. Pass threat_level and a short summary string.")
        store_tool = FunctionTool(store_call_result, description="Stores the final call analysis in MongoDB. Pass all analysis fields as arguments.")

        # --- Agent 1: Speech Agent ---
        speech_agent = AssistantAgent(
            name="Speech_Agent",
            description="Transcribes audio call recordings or extracts text from screenshots",
            system_message="""You are the Speech Agent. Your ONLY job is to obtain the text content from the provided input.

Instructions:
1. If an AUDIO file path is provided: Call `transcribe_audio` with the audio file path and report the full transcript.
2. If an IMAGE/SCREENSHOT file path is provided: Call `extract_image_text` with the image file path and report the extracted text.
3. If a transcript is already given directly, say: "TRANSCRIPT_PROVIDED: <transcript>"
4. End your response with: "SPEECH_DONE"

Do NOT analyse the content. Just extract the text.""",
            model_client=self.model,
            tools=[transcribe_tool, ocr_tool],
        )

        # --- Agent 2: Reasoning Agent ---
        reasoning_agent = AssistantAgent(
            name="Reasoning_Agent",
            description="Analyses transcript for scam patterns",
            system_message="""You are the Reasoning Agent. Your job is to detect scam patterns in the call transcript.

Instructions:
1. Extract the transcript text from the previous message.
2. Call the `analyze_transcript` tool with the full transcript text.
3. Report the returned JSON fields clearly:
   - threat_score (0-100)
   - fear_indicators (list of matched fear keywords)
   - authority_impersonation (list of matched authority keywords)
   - urgency_signals (list of urgency keywords)
   - financial_pressure (list of financial keywords)
4. Provide a 1-sentence LLM reasoning about WHY these indicate a scam (or not).
5. End your response with: "REASONING_DONE"

Be factual. Do not make a final decision yet.""",
            model_client=self.model,
            tools=[analyze_tool],
        )

        # --- Agent 3: Decision Agent ---
        decision_agent = AssistantAgent(
            name="Decision_Agent",
            description="Makes final threat determination",
            system_message="""You are the Decision Agent. Your job is to produce the final threat verdict.

Instructions:
1. Read the threat_score from the Reasoning Agent.
2. Call `get_threat_level` with that integer score.
3. Produce a final structured summary in this EXACT format:

FINAL_VERDICT:
- Threat Level: <SAFE|SUSPICIOUS|HIGH_RISK|CRITICAL>
- Threat Score: <0-100>
- Summary: <2-3 sentence plain English explanation for a senior citizen>
- Caller Type: <Scammer|Unknown|Legitimate>
- Recommendation: <What the senior should do right now>

4. End with: "DECISION_DONE" """,
            model_client=self.model,
            tools=[threat_level_tool],
        )

        # --- Agent 4: Action Agent ---
        action_agent = AssistantAgent(
            name="Action_Agent",
            description="Triggers alerts and stores results",
            system_message="""You are the Action Agent. Your job is to act on the verdict and archive results.

Instructions:
1. Read the FINAL_VERDICT from the Decision Agent.
2. Call `trigger_alert` with the threat_level and the summary text.
3. Call `store_call_result` with ALL the analysis fields collected across the pipeline.
   - transcript: full transcript from Speech Agent
   - summary: the Summary from Decision Agent
   - threat_level: from Decision Agent
   - threat_score: integer score from Reasoning Agent
   - fear_indicators, authority_indicators, urgency_indicators, financial_indicators: lists from Reasoning Agent
   - alert_sent: True if threat_level is HIGH_RISK or CRITICAL
   - language: detected language (from transcript tag if available, else "en")
4. Report all actions taken.
5. End with exactly: "GUARDIAN_ANGEL_COMPLETE" """,
            model_client=self.model,
            tools=[alert_tool, store_tool],
        )

        termination = TextMentionTermination("GUARDIAN_ANGEL_COMPLETE")

        return RoundRobinGroupChat(
            [speech_agent, reasoning_agent, decision_agent, action_agent],
            max_turns=8,
            termination_condition=termination,
        )

    async def reset(self):
        await self.team.reset()

    async def analyze(
        self,
        audio_path: Optional[str] = None,
        transcript: Optional[str] = None,
        image_path: Optional[str] = None,
    ):
        """
        Run the 4-agent pipeline.
        Provide audio_path, image_path, or transcript (raw text).
        Returns an async stream of events.
        """
        if audio_path:
            task = f"Analyze this call recording for scams. Audio file path: {audio_path}"
        elif image_path:
            task = (
                f"Analyze this screenshot for scams.\n\n"
                f"IMAGE FILE PATH: {image_path}\n\n"
                "Use extract_image_text to extract the text from the image, then analyze it for scam content."
            )
        elif transcript:
            task = (
                f"Analyze this call transcript for scams.\n\n"
                f"TRANSCRIPT:\n{transcript}\n\n"
                "Note: No audio file — skip transcription, the transcript is already provided."
            )
        else:
            raise ValueError("Provide audio_path, image_path, or transcript")

        return self.team.run_stream(task=task)
