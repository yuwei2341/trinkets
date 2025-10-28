"""
Main Gradio application for the ChatGPT clone.
"""
import gradio as gr
import os
from typing import List, Dict, Optional, Tuple
from conversation_manager import ConversationManager
from project_manager import ProjectManager
import config


class ChatGPTApp:
    """Main application class for the ChatGPT clone."""
    
    def __init__(self):
        """Initialize the application."""
        self.conversation_manager = ConversationManager(api_key=config.OPENAI_API_KEY)
        self.project_manager = ProjectManager(data_dir=config.DATA_DIR)
        
        # Application state
        self.current_project_id: Optional[str] = None
        self.current_conversation_id: Optional[str] = None
        
        # Mappings for dropdown display names to IDs
        self.project_name_to_id: Dict[str, str] = {}
        self.conversation_title_to_id: Dict[str, str] = {}
        
        # Create default project if none exist
        projects = self.project_manager.list_projects()
        if not projects:
            self.current_project_id = self.project_manager.create_project(
                name=config.DEFAULT_PROJECT_NAME,
                description="Default project for conversations"
            )
        else:
            self.current_project_id = projects[0]["id"]
    
    def create_new_conversation(
        self, 
        project_dropdown: str,
        model_dropdown: str,
        tools_checkboxes: List[str]
    ) -> Tuple[List, str, str, gr.Radio]:
        """
        Create a new conversation.
        
        Returns:
            Tuple of (chat_history, status_message, conversation_info, updated_conversation_dropdown)
        """
        # Create new conversation
        conv_id = self.conversation_manager.create_conversation(
            model=model_dropdown,
            tools=tools_checkboxes
        )
        self.current_conversation_id = conv_id
        
        # Add to current project
        self.project_manager.add_conversation(
            project_id=self.current_project_id,
            conversation_id=conv_id,
            title="New Conversation"
        )
        
        # Save the initial empty conversation immediately
        self._save_current_conversation()
        
        # Get updated conversation dropdown and reset selection
        updated_dropdown = self._get_conversation_list()
        
        return [], "New conversation created!", "Conversation: New Conversation", updated_dropdown
    
    def send_message(
        self, 
        message: str, 
        chat_history: List,
        temperature: float,
        max_tokens: int
    ) -> Tuple[List, str]:
        """
        Send a message and get response.
        
        Returns:
            Tuple of (updated_chat_history, empty_input)
        """
        if not message.strip():
            return chat_history, ""
        
        if not self.current_conversation_id:
            # Create a new conversation if none exists
            self.current_conversation_id = self.conversation_manager.create_conversation()
            self.project_manager.add_conversation(
                project_id=self.current_project_id,
                conversation_id=self.current_conversation_id,
                title=message[:50]  # Use first part of message as title
            )
        
        # Add user message to chat history
        chat_history.append({"role": "user", "content": message})
        
        # Get response from API
        response = self.conversation_manager.send_message(
            user_input=message,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Add assistant response to chat history
        if response["success"]:
            chat_history.append({"role": "assistant", "content": response["content"]})
            
            # Save conversation to project
            self._save_current_conversation()
        else:
            error_msg = f"Error: {response.get('error', 'Unknown error')}"
            chat_history.append({"role": "assistant", "content": error_msg})
        
        return chat_history, ""
    
    def _save_current_conversation(self):
        """Save current conversation to the current project."""
        if not self.current_conversation_id or not self.current_project_id:
            return
        
        # Get conversation data
        conversation_data = {
            "conversation_id": self.current_conversation_id,
            "model": self.conversation_manager.model,
            "tools": self.conversation_manager.tools,
            "metadata": self.conversation_manager.metadata,
            "messages": self.conversation_manager.messages
        }
        
        # Save to project
        self.project_manager.save_conversation_to_project(
            project_id=self.current_project_id,
            conversation_id=self.current_conversation_id,
            conversation_data=conversation_data
        )
    
    def load_conversation(self, conversation_name: str) -> Tuple[List, str, str]:
        """
        Load a conversation from the current project.
        
        Returns:
            Tuple of (chat_history, status_message, conversation_info)
        """
        if not conversation_name or conversation_name == "Select a conversation":
            return [], "No conversation selected", "No conversation"
        
        # Get conversation ID from mapping
        conv_id = self.conversation_title_to_id.get(conversation_name)
        if not conv_id:
            return [], "Invalid conversation selection", "No conversation"
        
        # Load conversation data
        conv_data = self.project_manager.load_conversation_from_project(
            project_id=self.current_project_id,
            conversation_id=conv_id
        )
        
        if not conv_data:
            return [], f"Failed to load conversation {conv_id}", "No conversation"
        
        # Restore conversation manager state
        self.current_conversation_id = conv_id
        self.conversation_manager.conversation_id = conv_id
        self.conversation_manager.model = conv_data.get("model", config.DEFAULT_MODEL)
        self.conversation_manager.tools = conv_data.get("tools", [])
        self.conversation_manager.metadata = conv_data.get("metadata", {})
        self.conversation_manager.messages = conv_data.get("messages", [])
        
        # Build chat history for display
        chat_history = []
        for msg in self.conversation_manager.messages:
            if msg["role"] in ["user", "assistant"]:
                chat_history.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        return chat_history, f"Loaded conversation: {conversation_name}", f"Conversation: {conversation_name}"
    
    def create_new_project(self, project_name: str, project_description: str) -> Tuple[gr.Dropdown, str]:
        """
        Create a new project.
        
        Returns:
            Tuple of (updated_project_dropdown, status_message)
        """
        if not project_name.strip():
            return self._get_project_dropdown(), "Project name cannot be empty"
        
        project_id = self.project_manager.create_project(
            name=project_name,
            description=project_description
        )
        
        self.current_project_id = project_id
        
        return self._get_project_dropdown(), f"Created project: {project_name}"
    
    def switch_project(self, project_name: str) -> Tuple[gr.Radio, str]:
        """
        Switch to a different project.
        
        Returns:
            Tuple of (updated_conversation_dropdown, status_message)
        """
        if not project_name or project_name == "Select a project":
            return self._get_conversation_list(), "No project selected"
        
        # Get project ID from mapping
        proj_id = self.project_name_to_id.get(project_name)
        if not proj_id:
            return self._get_conversation_list(), "Invalid project selection"
        
        self.current_project_id = proj_id
        
        # Clear current conversation
        self.current_conversation_id = None
        self.conversation_manager.clear_history()
        
        return self._get_conversation_list(), f"Switched to project: {project_name}"
    
    def _get_project_dropdown(self) -> gr.Dropdown:
        """Get updated project dropdown choices."""
        projects = self.project_manager.list_projects()
        
        # Clear and rebuild the mapping
        self.project_name_to_id.clear()
        
        choices = []
        for p in projects:
            name = p['name']
            # Handle duplicate names by appending a counter
            original_name = name
            counter = 1
            while name in self.project_name_to_id:
                name = f"{original_name} ({counter})"
                counter += 1
            
            self.project_name_to_id[name] = p['id']
            choices.append(name)
        
        # Find current selection by ID
        current_value = None
        if self.current_project_id:
            for name, proj_id in self.project_name_to_id.items():
                if proj_id == self.current_project_id:
                    current_value = name
                    break
        
        return gr.Dropdown(
            choices=["Select a project"] + choices,
            value=current_value or (choices[0] if choices else "Select a project"),
            label="Projects"
        )
    
    def _get_conversation_list(self) -> gr.Radio:
        """Get updated conversation list as Radio component."""
        if not self.current_project_id:
            return gr.Radio(choices=[], value=None, label="Conversations", interactive=True)
        
        conversations = self.project_manager.list_conversations(self.current_project_id)
        
        # Clear and rebuild the mapping
        self.conversation_title_to_id.clear()
        
        choices = []
        for c in conversations:
            title = c['title']
            # Handle duplicate titles by appending a counter
            original_title = title
            counter = 1
            while title in self.conversation_title_to_id:
                title = f"{original_title} ({counter})"
                counter += 1
            
            self.conversation_title_to_id[title] = c['id']
            choices.append(title)
        
        return gr.Radio(
            choices=choices,
            value=None,
            label="Conversations",
            interactive=True
        )
    
    def delete_conversation(self, conversation_name: str) -> Tuple[gr.Radio, str, List]:
        """
        Delete a conversation.
        
        Returns:
            Tuple of (updated_conversation_dropdown, status_message, empty_chat_history)
        """
        if not conversation_name or conversation_name == "Select a conversation":
            return self._get_conversation_list(), "No conversation selected", []
        
        # Get conversation ID from mapping
        conv_id = self.conversation_title_to_id.get(conversation_name)
        if not conv_id:
            return self._get_conversation_list(), "Invalid conversation selection", []
        
        # Delete conversation
        success = self.project_manager.remove_conversation(
            project_id=self.current_project_id,
            conversation_id=conv_id
        )
        
        if success:
            # Clear current conversation if it was deleted
            if self.current_conversation_id == conv_id:
                self.current_conversation_id = None
                self.conversation_manager.clear_history()
            
            return self._get_conversation_list(), f"Deleted conversation: {conversation_name}", []
        else:
            return self._get_conversation_list(), f"Failed to delete conversation", []
    
    def rename_conversation(self, conversation_name: str, new_title: str) -> Tuple[gr.Radio, str]:
        """
        Rename a conversation.
        
        Returns:
            Tuple of (updated_conversation_dropdown, status_message)
        """
        if not conversation_name or conversation_name == "Select a conversation":
            return self._get_conversation_list(), "No conversation selected"
        
        if not new_title.strip():
            return self._get_conversation_list(), "New title cannot be empty"
        
        # Get conversation ID from mapping
        conv_id = self.conversation_title_to_id.get(conversation_name)
        if not conv_id:
            return self._get_conversation_list(), "Invalid conversation selection"
        
        # Rename conversation
        success = self.project_manager.update_conversation_title(
            project_id=self.current_project_id,
            conversation_id=conv_id,
            new_title=new_title.strip()
        )
        
        if success:
            return self._get_conversation_list(), f"Renamed conversation to: {new_title}"
        else:
            return self._get_conversation_list(), "Failed to rename conversation"
    
    def clear_chat(self) -> Tuple[List, str]:
        """
        Clear current chat history.
        
        Returns:
            Tuple of (empty_chat_history, status_message)
        """
        self.conversation_manager.clear_history()
        return [], "Chat cleared"
    
    def build_interface(self) -> gr.Blocks:
        """Build and return the Gradio interface."""
        
        # Custom CSS to mimic ChatGPT font styling and sidebar
        custom_css = """
        /* ChatGPT-like font styling */
        * {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", 
                         "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", 
                         sans-serif !important;
        }
        
        /* Better text rendering */
        body {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        
        /* Chat message styling */
        .message {
            font-size: 16px;
            line-height: 1.5;
        }
        
        /* Input box styling */
        textarea {
            font-size: 16px;
        }
        
        /* Conversation list sidebar styling */
        .gr-radio-group {
            background-color: transparent !important;
            border: none !important;
            padding: 0 !important;
        }
        
        .gr-radio-group label {
            display: block !important;
            padding: 10px 12px !important;
            margin: 4px 0 !important;
            border-radius: 8px !important;
            cursor: pointer !important;
            transition: background-color 0.2s ease !important;
            border: 1px solid transparent !important;
        }
        
        .gr-radio-group label:hover {
            background-color: rgba(0, 0, 0, 0.05) !important;
        }
        
        .gr-radio-group input[type="radio"]:checked + label,
        .gr-radio-group label.selected {
            background-color: rgba(0, 0, 0, 0.1) !important;
            font-weight: 500 !important;
        }
        
        /* Hide radio buttons */
        .gr-radio-group input[type="radio"] {
            display: none !important;
        }
        
        /* Sidebar column styling */
        .gr-column:first-child {
            background-color: #f9f9f9;
            padding: 16px;
            border-right: 1px solid #e0e0e0;
        }
        """
        
        with gr.Blocks(title=config.APP_TITLE, theme=config.DEFAULT_THEME, css=custom_css) as app:
            gr.Markdown(f"# {config.APP_TITLE}")
            gr.Markdown(config.APP_DESCRIPTION)
            
            with gr.Row():
                # Left sidebar for projects and conversations
                with gr.Column(scale=1):
                    gr.Markdown("### Projects")
                    
                    with gr.Group():
                        project_dropdown = self._get_project_dropdown()
                        
                        with gr.Accordion("Create New Project", open=False):
                            new_project_name = gr.Textbox(
                                label="Project Name",
                                placeholder="Enter project name..."
                            )
                            new_project_desc = gr.Textbox(
                                label="Description",
                                placeholder="Enter project description...",
                                lines=3
                            )
                            create_project_btn = gr.Button("Create Project", variant="primary")
                    
                    gr.Markdown("### Conversations")
                    
                    with gr.Group():
                        conversation_list = self._get_conversation_list()
                        
                        with gr.Row():
                            delete_conv_btn = gr.Button("Delete", variant="stop", scale=1)
                            new_conv_btn = gr.Button("New Conversation", variant="primary", scale=1)
                        
                        with gr.Accordion("Rename Conversation", open=False):
                            new_conversation_title = gr.Textbox(
                                label="New Title",
                                placeholder="Enter new conversation title..."
                            )
                            rename_conv_btn = gr.Button("Rename", variant="secondary")
                
                # Main chat area
                with gr.Column(scale=3):
                    chatbot = gr.Chatbot(
                        label="Chat",
                        height=config.CHAT_HEIGHT,
                        type="messages"
                    )
                    
                    with gr.Row():
                        msg_input = gr.Textbox(
                            label="Message",
                            placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)",
                            lines=2,
                            scale=9,
                            submit_btn=True  # Enable submit on Enter
                        )
                        send_btn = gr.Button("Send", variant="primary", scale=1)
                    
                    clear_btn = gr.Button("Clear Chat", variant="secondary")
                    
                    status_box = gr.Textbox(
                        label="Status",
                        interactive=False,
                        lines=1
                    )
                
                # Right sidebar for settings
                with gr.Column(scale=1):
                    gr.Markdown("### Settings")
                    
                    model_dropdown = gr.Dropdown(
                        choices=config.AVAILABLE_MODELS,
                        value=config.DEFAULT_MODEL,
                        label="Model"
                    )
                    
                    tools_checkboxes = gr.CheckboxGroup(
                        choices=config.AVAILABLE_TOOLS,
                        label="Tools",
                        value=[]
                    )
                    
                    temperature_slider = gr.Slider(
                        minimum=0.0,
                        maximum=2.0,
                        value=config.DEFAULT_TEMPERATURE,
                        step=0.1,
                        label="Temperature"
                    )
                    
                    max_tokens_slider = gr.Slider(
                        minimum=256,
                        maximum=8192,
                        value=config.DEFAULT_MAX_TOKENS,
                        step=256,
                        label="Max Tokens"
                    )
                    
                    gr.Markdown("### Info")
                    conversation_info = gr.Textbox(
                        label="Current Conversation",
                        value="No conversation",
                        interactive=False
                    )
            
            # Event handlers
            
            # Send message
            send_btn.click(
                fn=self.send_message,
                inputs=[msg_input, chatbot, temperature_slider, max_tokens_slider],
                outputs=[chatbot, msg_input]
            )
            
            msg_input.submit(
                fn=self.send_message,
                inputs=[msg_input, chatbot, temperature_slider, max_tokens_slider],
                outputs=[chatbot, msg_input]
            )
            
            # New conversation
            new_conv_btn.click(
                fn=self.create_new_conversation,
                inputs=[project_dropdown, model_dropdown, tools_checkboxes],
                outputs=[chatbot, status_box, conversation_info, conversation_list]
            )
            
            # Auto-load conversation when selected from list
            conversation_list.change(
                fn=self.load_conversation,
                inputs=[conversation_list],
                outputs=[chatbot, status_box, conversation_info]
            )
            
            # Delete conversation
            delete_conv_btn.click(
                fn=self.delete_conversation,
                inputs=[conversation_list],
                outputs=[conversation_list, status_box, chatbot]
            )
            
            # Rename conversation
            rename_conv_btn.click(
                fn=self.rename_conversation,
                inputs=[conversation_list, new_conversation_title],
                outputs=[conversation_list, status_box]
            )
            
            # Clear chat
            clear_btn.click(
                fn=self.clear_chat,
                inputs=[],
                outputs=[chatbot, status_box]
            )
            
            # Create project
            create_project_btn.click(
                fn=self.create_new_project,
                inputs=[new_project_name, new_project_desc],
                outputs=[project_dropdown, status_box]
            )
            
            # Switch project
            project_dropdown.change(
                fn=self.switch_project,
                inputs=[project_dropdown],
                outputs=[conversation_list, status_box]
            )
        
        return app
    
    def launch(self, **kwargs):
        """Launch the Gradio application."""
        app = self.build_interface()
        app.launch(**kwargs)


def main():
    """Main entry point for the application."""
    # Check for API key
    if not config.OPENAI_API_KEY:
        print("Warning: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        print("\nOr create a .env file with:")
        print("  OPENAI_API_KEY=your-api-key-here")
    
    # Create and launch app
    app = ChatGPTApp()
    app.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860
    )


if __name__ == "__main__":
    main()
