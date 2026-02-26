# Guardian Angel: AI-Powered Scam Protection System

🦉 **Guardian Angel** is an AI-powered scam protection system designed to protect senior citizens from digital fraud and phone scams using advanced multi-agent workflows.

## 🌟 Overview

Guardian Angel uses specialized AI agents working together to analyze and detect scam attempts across two main channels:
- **Audio calls** - Recorded audio transcription and scam pattern detection
- **Screenshots/Images** - Visual content analysis for phishing and fraud

## 🚀 Features

### 📞 Audio Scam Detection
- **Recorded audio transcription** using OpenAI Whisper
- **4-agent pipeline** coordinated scam analysis
- **Senior-friendly interface** with clear threat indicators
- **Automated alerts** to family and authorities
- **Multi-language support** for global accessibility

### 📸 Image Scam Detection
- **OCR text extraction** from screenshots and images
- **7-agent coordinated analysis** using AutoGen framework:
  - OCR Specialist - Text extraction
  - Link Checker - URL safety verification
  - Content Analyst - Scam pattern recognition
  - Decision Maker - Risk assessment
  - Summary Agent - Result compilation
  - Language Translation - Multi-language support
  - Data Storage - Analysis persistence
- **Visual fraud detection** for phishing emails, fake banking alerts, and malicious pop-ups

## 📁 Project Structure

```
Guardian_Angel/
├── audio-scam-detection/          # Audio call scam detection
│   ├── agents_audio.py           # Audio analysis agents
│   ├── app.py                    # Gradio web interface
│   ├── requirements.txt          # Python dependencies
│   ├── config/                   # Agent configurations
│   ├── tools/                    # Audio-specific tools
│   │   ├── speech_transcriber.py # Audio transcription
│   │   ├── scam_detector.py      # Scam pattern detection
│   │   ├── alert_system.py       # Family/authority alerts
│   │   └── db_connector.py       # Database operations
│   └── TrainingData/             # Training datasets
│
└── image-scam-detection/          # Screenshot/image analysis
    ├── agents.py                 # Multi-agent pipeline
    ├── app.py                    # Gradio web interface
    ├── evaluation.py             # Performance evaluation
    ├── requirements.txt          # Python dependencies
    ├── config/                   # Agent configurations
    ├── tools/                    # Image-specific tools
    │   ├── image_ocr.py          # OCR text extraction
    │   ├── url_checker.py        # URL safety verification
    │   └── formatter.py          # Output formatting
    ├── evals/                    # Evaluation datasets
    └── examples/                 # Sample test images
```

## 🛠️ Technology Stack

- **AI Framework**: AutoGen 0.4.0 for multi-agent orchestration
- **LLM Integration**: OpenAI GPT models via Gemini API endpoint
- **Audio Processing**: OpenAI Whisper for transcription
- **Image Processing**: Gemini Vision for OCR and visual analysis
- **Web Interface**: Gradio for senior-friendly UI
- **Data Storage**: MongoDB for analysis persistence
- **Configuration**: YAML-based agent setup

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- Gemini API key (set as `GEMINI_API_KEY`)
- Required Python packages

### Audio Scam Detection
```bash
cd audio-scam-detection
pip install -r requirements.txt
python app.py
```
Access at: http://localhost:7861

### Image Scam Detection
```bash
cd image-scam-detection
pip install -r requirements.txt  
python app.py
```
Access at: http://localhost:7860

## 🎯 Use Cases

- **Senior Protection**: Easy-to-use interfaces for elderly users to verify suspicious calls and messages
- **Recorded Analysis**: Upload and analyze suspicious audio recordings and visual content
- **Family Safety**: Automated alerts to family members when high-risk scams are detected
- **Multi-language Support**: Analysis in user's native language for better comprehension
- **Educational Tool**: Visual demonstration of AI agent workflows for scam detection

## 🔧 Configuration

Both modules use YAML configuration files in their respective `config/` directories:
- **Agent prompts and behavior**
- **Detection sensitivity thresholds**
- **Alert escalation rules**
- **Model parameters and endpoints**

## 📊 Evaluation & Testing

The image detection module includes comprehensive evaluation tools:
- **Category-based testing**: Authority, commerce, financial, and opportunity scams
- **Performance metrics**: Accuracy, precision, recall across scam types
- **False positive analysis**: Legitimate content verification
- **Multi-language testing**: Evaluation across different languages

## 🤝 Contributing

Guardian Angel is designed to protect vulnerable populations from sophisticated scam attempts. Contributions that improve detection accuracy, enhance user experience, or expand language support are welcome.

## 👥 Collaborators

- **[muhammadnavas](https://github.com/muhammadnavas)**
- **[abdulreha](https://github.com/abdulreha)**

---

🔒 **Guardian Angel** — Protecting Senior Citizens from Digital Fraud
