# ChatGPT Clone

A modern ChatGPT-style application built with Python, using OpenAI's Responses API and Gradio for a clean, intuitive interface.

## Features

- **💬 Stateful Conversations** - Multi-turn conversations with automatic context management via OpenAI Responses API
- **📁 Project Organization** - Group conversations into projects for better organization
- **🎨 ChatGPT-Style UI** - Clean sidebar with conversation list, familiar chat interface
- **🛠️ Built-in Tools** - Web search, file search, and code interpreter support
- **⚙️ Customizable Settings** - Multiple models (GPT-5, GPT-4o, etc.), adjustable temperature and tokens
- **✏️ Conversation Management** - Create, rename, delete, and switch between conversations seamlessly
- **⌨️ Keyboard Shortcuts** - Press Enter to send messages, Shift+Enter for new lines

## Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key
export OPENAI_API_KEY='your-api-key-here'

# Run the app
python app.py
```

The app will launch at `http://localhost:7860`

## Usage

### Interface Overview

**Left Sidebar**
- **Projects**: Select or create projects to organize conversations
- **Conversations**: Clickable list of conversations in the current project
  - Click a conversation to load it instantly
  - Use "New Conversation" button to start fresh
  - Delete or rename conversations as needed

**Main Area**
- Chat interface with conversation history
- Type messages and press Enter to send
- Clear chat button to reset current view

**Right Sidebar**
- **Model**: Choose between GPT-5, GPT-4o, GPT-4 Turbo, etc.
- **Tools**: Enable web search, file search, or code interpreter
- **Temperature**: Control response creativity (0.0-2.0)
- **Max Tokens**: Set maximum response length (256-8192)
- **Info**: Shows current conversation name

### Key Features

**GPT-5 Support**
- Default model is GPT-5
- Temperature parameter automatically excluded for GPT-5 (as per API requirements)
- Full backward compatibility with other models

**Conversation List**
- All conversations visible in sidebar (no dropdown needed)
- Hover effects and selected state highlighting
- Auto-loads conversation on click
- Shows conversation titles, not IDs

**Auto-Save**
- Conversations automatically saved to disk
- Resume from where you left off
- All data stored as JSON in `data/` directory

## Project Structure

```
chatgpt/
├── app.py                    # Gradio UI and application logic
├── conversation_manager.py   # OpenAI Responses API integration
├── project_manager.py        # Project and conversation persistence
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
└── data/                     # Auto-generated storage
    ├── projects_index.json
    └── projects/
        └── {project_id}/
            ├── project.json
            └── {conversation_id}.json
```

## Configuration

Edit `config.py` to customize:

```python
DEFAULT_MODEL = "gpt-5"              # Default AI model
AVAILABLE_MODELS = [...]             # Models in dropdown
AVAILABLE_TOOLS = [...]              # Available tools
DEFAULT_TEMPERATURE = 1.0            # Default temperature
DEFAULT_MAX_TOKENS = 4096            # Default token limit
CHAT_HEIGHT = 600                    # Chat area height
DEFAULT_THEME = "soft"               # Gradio theme
```

## OpenAI Responses API

This app uses the newer **Responses API** (not Chat Completions API), which provides:
- Automatic conversation context management
- Built-in tool support (web search, file search, code interpreter)
- Simplified multi-turn conversation handling
- Structured response format with `output_text` convenience property

Learn more: [OpenAI Responses API Documentation](https://platform.openai.com/docs/guides/latest-model)

## Data Storage

All data is stored as JSON files in the `data/` directory:
- Easy to backup and version control
- Human-readable format
- Simple migration and export
- No database setup required

## Troubleshooting

**API Key Issues**
```bash
# Set your API key
export OPENAI_API_KEY='your-key-here'
# Or create .env file
echo "OPENAI_API_KEY=your-key-here" > .env
```

**Import Errors**
```bash
pip install -r requirements.txt
```

**Port Already in Use**
The app defaults to port 7860. Change it in `app.py`:
```python
app.launch(server_port=8080)  # Use different port
```

## Testing

The project includes comprehensive test coverage:
```bash
# Run conversation manager tests
python test_conversation_manager.py

# Check response extraction
python test_response_extraction.py
```

---

**Happy chatting! 🚀**
