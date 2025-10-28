"""
Configuration file for the ChatGPT clone application.
"""
import os
from typing import List

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Application Settings
APP_TITLE = "ChatGPT Clone"
APP_DESCRIPTION = "A ChatGPT clone using OpenAI Responses API and Gradio"

# Data Storage
DATA_DIR = "./data"
PROJECTS_DIR = "./data/projects"

# Model Settings
DEFAULT_MODEL = "gpt-5"
AVAILABLE_MODELS = [
    "gpt-5",
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
]

# Tool Settings
AVAILABLE_TOOLS = [
    "web_search",
    "file_search",
    "code_interpreter",
]

# Conversation Settings
DEFAULT_TEMPERATURE = 1.0
DEFAULT_MAX_TOKENS = 4096
MAX_CONVERSATION_HISTORY = 100

# UI Settings
CHAT_HEIGHT = 600
SIDEBAR_WIDTH = 300
DEFAULT_THEME = "soft"  # Gradio theme

# Streaming
ENABLE_STREAMING = True
STREAM_CHUNK_SIZE = 1024

# Project Settings
DEFAULT_PROJECT_NAME = "Default Project"
MAX_PROJECT_NAME_LENGTH = 100
MAX_CONVERSATION_TITLE_LENGTH = 200

# File Upload Settings (for file_search tool)
MAX_FILE_SIZE_MB = 100
ALLOWED_FILE_TYPES = [".txt", ".pdf", ".docx", ".py", ".js", ".html", ".css", ".json", ".xml", ".md"]
