# Excel-lent AI Interview Platform

An AI-powered technical interview platform specifically designed to assess any interview-concept skills through interactive conversations.

## System Requirements

- **CPU**: 8+ cores recommended for running local LLMs
- **RAM**: Minimum 16GB, 32GB recommended
- **GPU**: NVIDIA GPU with 8GB+ VRAM recommended for optimal performance
- **Storage**: 20GB+ free space for LLM models
- **Operating System**: macOS, Windows, or Linux

## Prerequisites

1. **LM Studio**
   - Download and install [LM Studio](https://lmstudio.ai/)
   - Launch LM Studio and download the recommended model:
     - Qwen3 8B (or similar 8-12B parameter models)
   - Start the local inference server in LM Studio (default port: 1234)

2. **Python**
   - Python 3.9 or higher
   - pip (Python package manager)

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/kaniac04/Excel-lentAI.git
cd Excel-lentAI
```

2. **Set up a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
.\venv\Scripts\activate  # On Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
- Update the following variables:
```
API_URL=http://localhost:8000
LLM_URL=http://localhost:1234/v1/chat/completions
LLM_MODEL=qwen3:8b
TAVILY_API_KEY=your_tavily_api_key
```

## Running the Application

1. **Start LM Studio**
   - Launch LM Studio
   - Load your chosen model
   - Start the local inference server

2. **Start the Backend Server**
```bash
python main.py
```

3. **Start the Streamlit Frontend**
```bash
streamlit run streamlit_ui.py
```

4. **Access the Application**
   - Open your browser and navigate to `http://localhost:8501`

## Features

- Multi-phase technical interviews
- Real-time web search for context
- Streaming responses
- Interactive chat interface
- Session management
- Colored logging
- Content moderation

## Architecture

- Frontend: Streamlit
- Backend: FastAPI
- LLM Interface: Local LM Studio server
- Web Search: Tavily API
- Session Management: In-memory storage
- Logging: Custom colored logger

## Notes

- Ensure LM Studio is running before starting the application
- The quality of interviews depends on the LLM model used
- Larger models provide better results but require more computational resources
- The application requires a stable internet connection for web searches

## License

MIT License
