# Docify - AI-Powered Voice Agent Platform

A sophisticated voice AI agent platform built with LiveKit, OpenAI, and modern web technologies. Docify enables real-time voice interactions with advanced features like barge-in handling, finite state machines, and comprehensive metrics collection.

## Features

- **Real-time Voice Processing**: Powered by LiveKit for low-latency voice communications
- **AI Integration**: OpenAI GPT models for intelligent conversation handling
- **Advanced Voice Features**:
  - Barge-in detection and handling
  - Voice Activity Detection (VAD)
  - Finite State Machine for conversation flow
  - Real-time transcription with Deepgram
- **Multi-language Support**: Python and Node.js implementations
- **Metrics & Analytics**: Comprehensive performance monitoring
- **Secure Configuration**: Environment-based API key management

## 📦 Project Structure

```
docify/
├── agent-python/          # Python implementation
│   ├── agent.py           # Main Python agent
│   ├── tools/             # Tool handlers and routing
│   └── .env.example       # Environment template
├── agent-starter-node/    # Node.js starter components
├── src/                   # Core TypeScript/JavaScript modules
│   ├── voice/             # Voice processing components
│   ├── tools/             # Tool system
│   └── dev/               # Development utilities
└── README.md              # This file
```

## 🛠️ Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- LiveKit account and API keys
- OpenAI API key
- Deepgram API key (optional, for transcription)

### Environment Configuration

1. Copy the environment template:
```bash
cp agent-python/.env.example agent-python/.env.local
```

2. Fill in your API keys:
```env
LIVEKIT_URL=wss://your-livekit-instance.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
OPENAI_API_KEY=your_openai_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
```

### Python Setup

```bash
cd agent-python
pip install -r pyproject.toml
python agent.py
```

### Node.js Setup

```bash
cd agent-starter-node
npm install
npm start
```

## 🔧 Core Components

### Voice Agent (`src/voice/agent.ts`)
- Main orchestrator for voice interactions
- Handles conversation state and flow control
- Integrates with AI models for response generation

### Finite State Machine (`src/voice/fsm.ts`)
- Manages conversation states (listening, thinking, speaking)
- Handles state transitions and validation
- Provides hooks for custom state logic

### Barge-in Handler (`src/voice/bargeIn.ts`)
- Detects user interruptions during agent speech
- Provides smooth conversation flow
- Configurable sensitivity settings

### Metrics Collection (`src/voice/metrics.ts`)
- Tracks performance metrics
- Monitors conversation quality
- Provides analytics for optimization

### Tool System (`src/tools/`)
- Extensible tool architecture
- Handler registration and routing
- Schema validation for tool inputs

## 🚦 Getting Started

1. **Clone the repository**
```bash
git clone git@github.com:abdulrehman-11/Docify.git
cd Docify
```

2. **Set up environment variables**
```bash
cp agent-python/.env.example agent-python/.env.local
# Edit .env.local with your API keys
```

3. **Run the Python agent**
```bash
cd agent-python
python agent.py
```

4. **Test with development utilities**
```bash
# Run mock tests
cd src/dev
node mockRun.ts
```

## 📊 Features in Detail

### Voice Processing Pipeline
1. **Audio Input**: Capture from microphone or streaming source
2. **VAD Processing**: Detect speech activity
3. **Transcription**: Convert speech to text (Deepgram/OpenAI)
4. **AI Processing**: Generate intelligent responses
5. **TTS Generation**: Convert responses to speech
6. **Audio Output**: Deliver to speakers or stream

### State Management
- **Idle**: Waiting for user input
- **Listening**: Actively receiving audio
- **Processing**: AI generating response
- **Speaking**: Agent delivering response
- **Interrupted**: Handling barge-in events

## 🔒 Security

- API keys stored in environment variables
- `.env.local` files excluded from version control
- Secure communication with LiveKit servers
- Rate limiting and abuse protection

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## Acknowledgments

- [LiveKit](https://livekit.io/) for real-time communication infrastructure
- [OpenAI](https://openai.com/) for advanced AI capabilities
- [Deepgram](https://deepgram.com/) for speech recognition services


---
