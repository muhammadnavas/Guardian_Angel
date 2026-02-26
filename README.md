# Guardian Angel: AI-Powered Scam Protection System

🦉 Guardian Angel is a comprehensive AI-powered scam protection system that uses Multi-Agent workflows to detect and analyze potential scam attempts across different mediums. The system provides senior-friendly interfaces and real-time analysis to help protect users from various types of scams.

## 🚀 Features

### 🎵 Audio Scam Detection
- **Real-time audio call analysis** with AI transcription
- **4-agent agentic pipeline** for comprehensive scam detection
- **Senior-friendly interface** with clear visual feedback
- **Multi-language support** for global accessibility

### 📷 Image Scam Detection  
- **Screenshot and image analysis** for visual scam detection
- **7-agent AutoGen team** working in coordinated fashion:
  - OCR Specialist
  - Link Checker  
  - Content Analyst
  - Decision Maker
  - Summary Specialist
  - Language Translation Specialist
  - Data Storage Agent
- **Multi-language analysis** with results in extracted text language
- **URL verification** and suspicious link detection

## 📁 Project Structure

```
Guardian_Angel/
├── audio-scam-detection/          # Audio call scam detection system
│   ├── agents_audio.py           # Audio-specific agent implementations
│   ├── agents_screenshot.py      # Screenshot analysis agents
│   ├── app.py                    # Gradio web interface
│   ├── requirements.txt          # Python dependencies
│   ├── config/                   # Agent configuration files
│   ├── tools/                    # Detection and analysis tools
│   └── TrainingData/             # Training datasets
│
└── image-scam-detection/          # Screenshot/image scam detection
    ├── agents.py                 # Agent implementations
    ├── app.py                    # Gradio web interface  
    ├── evaluation.py             # Model evaluation tools
    ├── requirements.txt          # Python dependencies
    ├── config/                   # Agent configuration
    ├── tools/                    # OCR, URL checking, formatting tools
    ├── evals/                    # Evaluation datasets and experiments
    └── examples/                 # Sample scam images for testing
```

## 🛠️ Technology Stack

- **AI Framework**: AutoGen 0.4.0 for multi-agent coordination
- **LLM Integration**: OpenAI GPT models for natural language processing
- **Audio Processing**: OpenAI Whisper, librosa, soundfile
- **Image Processing**: PIL (Pillow), OCR capabilities
- **Web Interface**: Gradio for user-friendly interfaces
- **Data Storage**: MongoDB for persistence
- **Configuration**: YAML-based agent configuration

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- Required Python packages (see requirements.txt in each module)

### Audio Scam Detection Setup
```bash
cd audio-scam-detection
pip install -r requirements.txt
python app.py
```

### Image Scam Detection Setup
```bash
cd image-scam-detection  
pip install -r requirements.txt
python app.py
```

## 🎯 Use Cases

- **Elderly Protection**: Senior-friendly interfaces to help older adults identify scam calls and messages
- **Real-time Analysis**: Instant feedback on suspicious audio calls or images/screenshots
- **Educational Tool**: Visual workflow demonstration showing how AI agents analyze potential scams
- **Multi-language Support**: Automatic language detection and analysis in user's preferred language

## 🔧 Configuration

Each module contains YAML configuration files in the `config/` directory to customize:
- Agent behavior and prompts
- Detection thresholds and criteria  
- LLM model selection and parameters
- Logging and output formatting

## 📊 Evaluation

The image-scam-detection module includes comprehensive evaluation tools with test datasets across multiple scam categories:
- Authority scams
- Commerce/shopping scams  
- Customer service impersonation
- Financial fraud attempts
- Opportunity/reward scams

## 🤝 Contributing

Guardian Angel is designed to protect vulnerable users from increasingly sophisticated scam attempts. Contributions that improve detection accuracy, expand language support, or enhance user experience are welcome.

## 📄 License

This project is designed for scam protection and educational purposes. Please use responsibly and in accordance with local laws and regulations.
