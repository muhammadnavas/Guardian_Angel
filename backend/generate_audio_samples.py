"""
Generate synthetic demo audio samples for Guardian Angel hackathon demo.
Uses pyttsx3 (offline TTS) if available, otherwise generates WAV stubs
with companion .txt transcript files as a fallback.
"""

import os
import wave
import struct
import math

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio_samples")
os.makedirs(AUDIO_DIR, exist_ok=True)

SAMPLES = {
    "scam_cbi_arrest.wav": (
        "Hello, I am Inspector Rajesh Kumar from CBI Cybercrime Division. "
        "Your Aadhaar number has been used in illegal drug trafficking. "
        "A warrant has been issued for your arrest. "
        "You must pay a security deposit of two lakh rupees immediately to avoid being detained. "
        "Do not hang up or we will send police to your house within one hour. "
        "Transfer the money to this account right now. This is your last warning."
    ),
    "scam_customs_parcel.wav": (
        "This is TRAI Telecom Authority calling. "
        "A parcel in your name has been seized at customs containing suspicious documents. "
        "Our officer will connect you to the Enforcement Directorate. "
        "You must pay a fine of fifty thousand rupees today to clear your name. "
        "Your bank account will be frozen if you delay any further."
    ),
    "scam_bank_impersonation.wav": (
        "Hello sir, I am calling from SBI bank customer care. "
        "Your account shows some unusual activity today. "
        "To protect your account we need you to verify your identity. "
        "Please share your OTP and account number to avoid account suspension."
    ),
    "safe_doctor_reminder.wav": (
        "Hello, this is a reminder call from City Hospital. "
        "Your appointment with Doctor Sharma is scheduled for tomorrow at three PM. "
        "Please arrive fifteen minutes early and bring your previous reports. "
        "For any queries please call our helpline. Thank you and have a nice day."
    ),
}


def generate_with_tts() -> bool:
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)
        engine.setProperty("volume", 1.0)
        voices = engine.getProperty("voices")
        if voices:
            engine.setProperty("voice", voices[0].id)
        for filename, text in SAMPLES.items():
            out_path = os.path.join(AUDIO_DIR, filename)
            if not os.path.exists(out_path):
                print(f"  [TTS] Generating {filename}...")
                engine.save_to_file(text, out_path)
        engine.runAndWait()
        return True
    except Exception as e:
        print(f"  pyttsx3 not available ({e}), using WAV stub fallback")
        return False


def generate_stub_wav(out_path: str, duration_secs: float = 10.0):
    """Create a tone WAV so Whisper knows it is an audio file."""
    sample_rate = 16000
    num_samples = int(sample_rate * duration_secs)
    with wave.open(out_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        data = struct.pack("<" + "h" * num_samples, *[
            int(200 * math.sin(2 * math.pi * 440 * i / sample_rate))
            for i in range(num_samples)
        ])
        wf.writeframes(data)


def generate_stubs():
    for filename, text in SAMPLES.items():
        wav_path = os.path.join(AUDIO_DIR, filename)
        txt_path = wav_path.replace(".wav", ".txt")
        if not os.path.exists(wav_path):
            print(f"  [GEN] Generating stub {filename}...")
            generate_stub_wav(wav_path)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"  [OK]  {filename} + .txt saved")


if __name__ == "__main__":
    print("\nGuardian Angel -- Audio Sample Generator")
    print("=" * 50)
    success = generate_with_tts()
    if not success:
        print("\nGenerating stub WAV files with transcript .txt companions...")
        generate_stubs()
    print(f"\nAudio samples ready in: {AUDIO_DIR}")
    print("Files:")
    for f in sorted(os.listdir(AUDIO_DIR)):
        path = os.path.join(AUDIO_DIR, f)
        size = os.path.getsize(path)
        print(f"  - {f} ({size:,} bytes)")
    print()
