"""
Conversation Manager for handling stateful conversations with OpenAI Responses API.
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from openai import OpenAI


class ConversationManager:
    """Manages conversations using OpenAI Responses API with stateful history."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the conversation manager.
        
        Args:
            api_key: OpenAI API key. If None, will use OPENAI_API_KEY environment variable.
        """
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
        self.conversation_id: Optional[str] = None
        self.messages: List[Dict[str, str]] = []
        self.model: str = "gpt-5"  # Default model
        self.tools: List[str] = []  # Tools like web_search, file_search
        self.metadata: Dict[str, Any] = {}
        
    def create_conversation(
        self, 
        model: str = "gpt-5",
        tools: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new conversation.
        
        Args:
            model: The model to use (e.g., "gpt-5", "gpt-4o", "gpt-4-turbo")
            tools: List of tools to enable (e.g., ["web_search", "file_search"])
            metadata: Additional metadata for the conversation
            
        Returns:
            conversation_id: Unique identifier for the conversation
        """
        self.model = model
        self.tools = tools or []
        self.metadata = metadata or {}
        self.messages = []
        
        # Generate a unique conversation ID
        self.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        self.metadata['created_at'] = datetime.now().isoformat()
        self.metadata['model'] = model
        
        return self.conversation_id
    
    def send_message(
        self, 
        user_input: str,
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send a message in the conversation using Responses API.
        
        Args:
            user_input: The user's message
            stream: Whether to stream the response
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            
        Returns:
            Response dictionary with message content and metadata
        """
        if not self.conversation_id:
            self.create_conversation()
        
        # Add user message to history
        self.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Prepare the request parameters
        params = {
            "model": self.model,
            "input": user_input,
        }
        
        # Add optional parameters
        # Note: GPT-5 doesn't support the temperature parameter
        if temperature is not None and self.model != "gpt-5":
            params["temperature"] = temperature
        if max_tokens is not None:
            params["max_output_tokens"] = max_tokens  # Responses API uses max_output_tokens
        
        # Add tools if specified (convert string names to proper tool objects)
        if self.tools:
            params["tools"] = [{"type": tool} for tool in self.tools]
        
        # Include conversation history as context
        # Build context from previous messages and include it in the input
        if len(self.messages) > 1:
            # Build context from previous messages
            context = self._build_context()
            if context:
                # Prepend context to the input
                params["input"] = f"{context}\n\nUser: {user_input}"
        
        # Call the Responses API
        if stream:
            response = self.client.responses.create(**params, stream=True)
            return self._handle_streaming_response(response)
        else:
            response = self.client.responses.create(**params)
            return self._handle_response(response)            
    
    def _build_context(self) -> Optional[str]:
        """
        Build context string from conversation history.
        
        Returns:
            Context string or None
        """
        if len(self.messages) <= 1:
            return None
        
        # Build context from previous messages (excluding the last user message)
        context_parts = []
        for msg in self.messages[:-1]:
            if msg["role"] in ["user", "assistant"]:
                context_parts.append(f"{msg['role']}: {msg['content']}")
        
        return "\n".join(context_parts) if context_parts else None
    
    def _handle_response(self, response: Any) -> Dict[str, Any]:
        """
        Handle non-streaming response from Responses API.
        
        Args:
            response: Response object from OpenAI
            
        Returns:
            Processed response dictionary
        """
   
        # Extract content from response
        # The exact structure depends on the Responses API format
        content = self._extract_content(response)
        
        # Add assistant message to history
        self.messages.append({
            "role": "assistant",
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "success": True,
            "content": content,
            "message_count": len(self.messages)
        }

    
    def _handle_streaming_response(self, response_stream: Any) -> Dict[str, Any]:
        """
        Handle streaming response from Responses API.
        
        Args:
            response_stream: Streaming response from OpenAI
            
        Returns:
            Generator yielding response chunks
        """
        full_content = []
        
        for chunk in response_stream:
            chunk_content = self._extract_content(chunk)
            if chunk_content:
                full_content.append(chunk_content)
                yield {
                    "success": True,
                    "content": chunk_content,
                    "is_chunk": True
                }
        
        # Add complete message to history
        complete_content = "".join(full_content)
        self.messages.append({
            "role": "assistant",
            "content": complete_content,
            "timestamp": datetime.now().isoformat()
        })
        
        yield {
            "success": True,
            "content": complete_content,
            "is_complete": True,
            "message_count": len(self.messages)
        }

    
    def _extract_content(self, response: Any) -> str:
        """
        Extract text content from response object.
        
        Args:
            response: Response from OpenAI Responses API
            
        Returns:
            Extracted text content as a plain string
        """
        # Handle Responses API structure
        # The SDK provides a convenient output_text property that aggregates text from output array
        
        # First try: use output_text convenience property (SDK-only, recommended)
        if hasattr(response, 'output_text') and response.output_text is not None:
            return str(response.output_text)
        
        # Second try: manually parse output array
        if hasattr(response, 'output') and response.output:
            output_list = response.output
            
            # output is a list of messages
            if isinstance(output_list, list) and len(output_list) > 0:
                first_message = output_list[0]
                
                # Check if message has content list
                if hasattr(first_message, 'content') and first_message.content:
                    content_list = first_message.content
                    
                    # content is a list of text objects
                    if isinstance(content_list, list) and len(content_list) > 0:
                        first_content = content_list[0]
                        
                        # Get the text attribute
                        if hasattr(first_content, 'text'):
                            return str(first_content.text)
                        else:
                            return str(first_content)
                    elif isinstance(content_list, str):
                        return content_list
                    else:
                        return str(content_list)
                
                # Fallback: stringify the message
                return str(first_message)            
        
        # Last resort: convert entire response to string
        return str(response)
        
    def get_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history.
        
        Returns:
            List of message dictionaries
        """
        return self.messages.copy()
    
    def clear_history(self):
        """Clear conversation history while keeping the conversation ID."""
        self.messages = []
    
    def save_conversation(self, filepath: str):
        """
        Save conversation to a JSON file.
        
        Args:
            filepath: Path to save the conversation
        """
        conversation_data = {
            "conversation_id": self.conversation_id,
            "model": self.model,
            "tools": self.tools,
            "metadata": self.metadata,
            "messages": self.messages
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)
    
    def load_conversation(self, filepath: str):
        """
        Load conversation from a JSON file.
        
        Args:
            filepath: Path to the conversation file
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            conversation_data = json.load(f)
        
        self.conversation_id = conversation_data.get("conversation_id")
        self.model = conversation_data.get("model", "gpt-5")
        self.tools = conversation_data.get("tools", [])
        self.metadata = conversation_data.get("metadata", {})
        self.messages = conversation_data.get("messages", [])
    
    def set_model(self, model: str):
        """
        Change the model for the conversation.
        
        Args:
            model: Model name (e.g., "gpt-5", "gpt-4o", "gpt-4-turbo")
        """
        self.model = model
        self.metadata['model'] = model
    
    def set_tools(self, tools: List[str]):
        """
        Set tools for the conversation.
        
        Args:
            tools: List of tool names (e.g., ["web_search", "file_search"])
        """
        self.tools = tools
    
    def get_message_count(self) -> int:
        """Get the number of messages in the conversation."""
        return len(self.messages)
    
    def get_last_message(self) -> Optional[Dict[str, str]]:
        """Get the last message in the conversation."""
        return self.messages[-1] if self.messages else None
