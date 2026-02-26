"""
OpenAI Whisper Speech-to-Text Transcriber

Uses librosa for audio loading (no FFmpeg required) and passes the numpy
array directly to Whisper's transcribe() interface.  This avoids the
subprocess-based FFmpeg call that fails on Windows when FFmpeg is absent.
"""

import os
import whisper
import librosa
import numpy as np


class SpeechTranscriber:
    """Handles speech-to-text transcription using OpenAI Whisper."""

    def __init__(self, model_size: str = "base"):
        """Initialize Whisper model.

        Args:
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large').
                        'base' is a good balance of speed and accuracy.
        """
        print(f"🔄 Loading Whisper {model_size} model...")
        self.model = whisper.load_model(model_size)
        print("✅ Whisper model loaded successfully")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def transcribe(self, audio_path: str) -> str:
        """Transcribe an audio file to text using OpenAI Whisper.

        Loads audio via librosa (no FFmpeg required) and passes a numpy
        float32 array directly to Whisper.  Falls back to Whisper's native
        loader (which needs FFmpeg) only as a last resort.

        Args:
            audio_path: Path to audio file (.wav, .mp3, .m4a, .ogg, etc.)

        Returns:
            Transcribed text: "[Language: <lang>]\\n<text>",
            "NO_SPEECH_FOUND" if the audio is silent,
            or an error string on failure.
        """
        audio_path = str(audio_path).strip()

        if not os.path.exists(audio_path):
            return f"Error: Audio file not found at {audio_path}"

        print(f"🎵 Loading audio: {os.path.basename(audio_path)}")
        print("🤖 Transcribing with Whisper...")

        # Primary path: librosa → numpy array → Whisper (no FFmpeg)
        try:
            audio_data, _ = librosa.load(audio_path, sr=16000, mono=True)
            result = self.model.transcribe(audio_data)
            text = result.get("text", "").strip()
            language = result.get("language", "unknown")

            if not text:
                print("⚠️ No speech detected in audio file")
                return "NO_SPEECH_FOUND"

            print(f"✅ Transcription complete ({language})")
            print(f"📝 Text preview: {text[:100]}...")
            return f"[Language: {language}]\n{text}"

        except Exception as primary_err:
            import traceback
            print(f"❌ librosa path failed: {traceback.format_exc()}")

            # Fallback: Whisper's native loader (requires FFmpeg)
            try:
                print("🔄 Trying Whisper native loader as fallback...")
                result = self.model.transcribe(audio_path, verbose=False)
                text = result.get("text", "").strip()
                language = result.get("language", "unknown")

                if not text:
                    return "NO_SPEECH_FOUND"

                print(f"✅ Fallback transcription successful ({language})")
                return f"[Language: {language}]\n{text}"

            except Exception as fallback_err:
                print(f"❌ All transcription paths failed: {fallback_err}")
                return (
                    f"Error in transcription: Could not load audio file "
                    f"{os.path.basename(audio_path)}. "
                    "Install FFmpeg (https://ffmpeg.org/download.html) or "
                    "use WAV/OGG files which librosa can decode natively."
                )

    def transcribe_with_segments(self, audio_path: str) -> dict:
        """Transcribe audio with timestamp segments for detailed analysis.

        Args:
            audio_path: Path to audio file

        Returns:
            Dict with 'text', 'language', and 'segments' (timestamped chunks),
            or {'error': ...} on failure.
        """
        if not os.path.exists(audio_path):
            return {"error": f"Audio file not found at {audio_path}"}

        def _build_segments(result: dict) -> list:
            return [
                {
                    "start": round(seg["start"], 1),
                    "end": round(seg["end"], 1),
                    "text": seg["text"].strip(),
                }
                for seg in result.get("segments", [])
            ]

        # Primary path: librosa → Whisper (no FFmpeg)
        try:
            audio_data, _ = librosa.load(audio_path, sr=16000, mono=True)
            result = self.model.transcribe(audio_data)
            return {
                "text": result.get("text", "").strip(),
                "language": result.get("language", "unknown"),
                "segments": _build_segments(result),
            }

        except Exception as primary_err:
            # Fallback: Whisper's native loader (requires FFmpeg)
            try:
                result = self.model.transcribe(audio_path)
                return {
                    "text": result.get("text", "").strip(),
                    "language": result.get("language", "unknown"),
                    "segments": _build_segments(result),
                }
            except Exception as e:
                return {"error": f"Error in transcription: {str(e)}"}
