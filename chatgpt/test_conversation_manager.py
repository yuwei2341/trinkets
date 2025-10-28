"""
Test script for ConversationManager.

This script tests the ConversationManager class functionality including:
- Conversation creation
- Message handling
- Model configuration
- File save/load operations
- GPT-5 specific behavior (temperature parameter exclusion)
"""
import os
import sys
import json
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path if running directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conversation_manager import ConversationManager


class TestConversationManager(unittest.TestCase):
    """Test suite for ConversationManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock the OpenAI client to avoid real API calls
        with patch('conversation_manager.OpenAI'):
            self.manager = ConversationManager(api_key="test_key")
        
        # Create a temporary directory for file operations
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after each test method."""
        # Remove temporary files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization_default_values(self):
        """Test that ConversationManager initializes with correct defaults."""
        with patch('conversation_manager.OpenAI'):
            manager = ConversationManager()
        
        self.assertIsNone(manager.conversation_id)
        self.assertEqual(manager.messages, [])
        self.assertEqual(manager.model, "gpt-5")
        self.assertEqual(manager.tools, [])
        self.assertEqual(manager.metadata, {})
    
    def test_create_conversation_default_model(self):
        """Test creating a conversation with default GPT-5 model."""
        conv_id = self.manager.create_conversation()
        
        self.assertIsNotNone(conv_id)
        self.assertTrue(conv_id.startswith("conv_"))
        self.assertEqual(self.manager.model, "gpt-5")
        self.assertEqual(self.manager.messages, [])
        self.assertIn('created_at', self.manager.metadata)
        self.assertEqual(self.manager.metadata['model'], "gpt-5")
    
    def test_create_conversation_custom_model(self):
        """Test creating a conversation with a custom model."""
        conv_id = self.manager.create_conversation(model="gpt-4o")
        
        self.assertEqual(self.manager.model, "gpt-4o")
        self.assertEqual(self.manager.metadata['model'], "gpt-4o")
    
    def test_create_conversation_with_tools(self):
        """Test creating a conversation with tools enabled."""
        tools = ["web_search", "file_search"]
        conv_id = self.manager.create_conversation(tools=tools)
        
        self.assertEqual(self.manager.tools, tools)
    
    def test_create_conversation_with_metadata(self):
        """Test creating a conversation with custom metadata."""
        metadata = {"project": "test_project", "user": "test_user"}
        conv_id = self.manager.create_conversation(metadata=metadata)
        
        self.assertIn('project', self.manager.metadata)
        self.assertEqual(self.manager.metadata['project'], "test_project")
    
    def test_set_model(self):
        """Test changing the model after initialization."""
        self.manager.create_conversation()
        self.manager.set_model("gpt-4o-mini")
        
        self.assertEqual(self.manager.model, "gpt-4o-mini")
        self.assertEqual(self.manager.metadata['model'], "gpt-4o-mini")
    
    def test_set_tools(self):
        """Test setting tools after initialization."""
        self.manager.create_conversation()
        tools = ["code_interpreter"]
        self.manager.set_tools(tools)
        
        self.assertEqual(self.manager.tools, tools)
    
    def test_send_message_creates_conversation_if_none(self):
        """Test that send_message creates a conversation if none exists."""
        # Mock the API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response"
        
        self.manager.client.responses.create = Mock(return_value=mock_response)
        
        # Conversation ID should be None initially
        self.assertIsNone(self.manager.conversation_id)
        
        # Send a message (which should create a conversation)
        result = self.manager.send_message("Hello")
        
        # Now conversation_id should be set
        self.assertIsNotNone(self.manager.conversation_id)
    
    def test_send_message_gpt5_excludes_temperature(self):
        """Test that temperature parameter is excluded for GPT-5."""
        self.manager.create_conversation(model="gpt-5")
        
        # Mock the API call
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response"
        
        self.manager.client.responses.create = Mock(return_value=mock_response)
        
        # Send message with temperature
        self.manager.send_message("Hello", temperature=0.7)
        
        # Check that the API was called
        self.manager.client.responses.create.assert_called_once()
        
        # Get the arguments passed to the API call
        call_args = self.manager.client.responses.create.call_args
        params = call_args[1] if call_args[1] else call_args[0][0] if call_args[0] else {}
        
        # Temperature should not be in params for GPT-5
        self.assertNotIn("temperature", params)
    
    def test_send_message_gpt4o_includes_temperature(self):
        """Test that temperature parameter is included for GPT-4o."""
        self.manager.create_conversation(model="gpt-4o")
        
        # Mock the API call
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response"
        
        self.manager.client.responses.create = Mock(return_value=mock_response)
        
        # Send message with temperature
        self.manager.send_message("Hello", temperature=0.7)
        
        # Check that the API was called
        self.manager.client.responses.create.assert_called_once()
        
        # Get the arguments passed to the API call
        call_args = self.manager.client.responses.create.call_args
        params = call_args[1] if call_args[1] else {}
        
        # Temperature should be in params for GPT-4o
        self.assertIn("temperature", params)
        self.assertEqual(params["temperature"], 0.7)
    
    def test_send_message_uses_max_output_tokens(self):
        """Test that max_tokens is converted to max_output_tokens."""
        self.manager.create_conversation()
        
        # Mock the API call
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response"
        
        self.manager.client.responses.create = Mock(return_value=mock_response)
        
        # Send message with max_tokens
        self.manager.send_message("Hello", max_tokens=100)
        
        # Get the arguments passed to the API call
        call_args = self.manager.client.responses.create.call_args
        params = call_args[1] if call_args[1] else {}
        
        # Should use max_output_tokens
        self.assertIn("max_output_tokens", params)
        self.assertEqual(params["max_output_tokens"], 100)
    
    def test_send_message_tools_format(self):
        """Test that tools are converted to proper format."""
        self.manager.create_conversation(tools=["web_search", "file_search"])
        
        # Mock the API call
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test response"
        
        self.manager.client.responses.create = Mock(return_value=mock_response)
        
        # Send message
        self.manager.send_message("Hello")
        
        # Get the arguments passed to the API call
        call_args = self.manager.client.responses.create.call_args
        params = call_args[1] if call_args[1] else {}
        
        # Tools should be in proper format
        self.assertIn("tools", params)
        expected_tools = [{"type": "web_search"}, {"type": "file_search"}]
        self.assertEqual(params["tools"], expected_tools)
    
    def test_get_history(self):
        """Test getting conversation history."""
        self.manager.create_conversation()
        
        # Add some messages manually
        self.manager.messages.append({"role": "user", "content": "Hello"})
        self.manager.messages.append({"role": "assistant", "content": "Hi there"})
        
        history = self.manager.get_history()
        
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["content"], "Hello")
        self.assertEqual(history[1]["content"], "Hi there")
        
        # Verify it returns a copy of the list (but shallow copy of dicts)
        # Modifying the list should not affect original
        history.append({"role": "user", "content": "New"})
        self.assertEqual(len(self.manager.messages), 2)  # Original unchanged
    
    def test_clear_history(self):
        """Test clearing conversation history."""
        self.manager.create_conversation()
        
        # Add some messages
        self.manager.messages.append({"role": "user", "content": "Hello"})
        self.manager.messages.append({"role": "assistant", "content": "Hi"})
        
        conv_id = self.manager.conversation_id
        
        # Clear history
        self.manager.clear_history()
        
        # Messages should be empty but conversation_id should remain
        self.assertEqual(len(self.manager.messages), 0)
        self.assertEqual(self.manager.conversation_id, conv_id)
    
    def test_get_message_count(self):
        """Test getting message count."""
        self.manager.create_conversation()
        
        self.assertEqual(self.manager.get_message_count(), 0)
        
        self.manager.messages.append({"role": "user", "content": "Hello"})
        self.assertEqual(self.manager.get_message_count(), 1)
        
        self.manager.messages.append({"role": "assistant", "content": "Hi"})
        self.assertEqual(self.manager.get_message_count(), 2)
    
    def test_get_last_message(self):
        """Test getting the last message."""
        self.manager.create_conversation()
        
        # No messages yet
        self.assertIsNone(self.manager.get_last_message())
        
        # Add a message
        self.manager.messages.append({"role": "user", "content": "First"})
        self.assertEqual(self.manager.get_last_message()["content"], "First")
        
        # Add another message
        self.manager.messages.append({"role": "assistant", "content": "Second"})
        self.assertEqual(self.manager.get_last_message()["content"], "Second")
    
    def test_save_conversation(self):
        """Test saving conversation to a file."""
        self.manager.create_conversation(model="gpt-5", tools=["web_search"])
        self.manager.messages.append({"role": "user", "content": "Hello"})
        
        filepath = os.path.join(self.temp_dir, "test_conversation.json")
        self.manager.save_conversation(filepath)
        
        # Verify file exists
        self.assertTrue(os.path.exists(filepath))
        
        # Verify file content
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data["model"], "gpt-5")
        self.assertEqual(data["tools"], ["web_search"])
        self.assertEqual(len(data["messages"]), 1)
        self.assertEqual(data["messages"][0]["content"], "Hello")
    
    def test_load_conversation(self):
        """Test loading conversation from a file."""
        # Create test data
        test_data = {
            "conversation_id": "test_conv_123",
            "model": "gpt-4o",
            "tools": ["file_search"],
            "metadata": {"test": "value"},
            "messages": [
                {"role": "user", "content": "Test message"}
            ]
        }
        
        filepath = os.path.join(self.temp_dir, "test_load.json")
        with open(filepath, 'w') as f:
            json.dump(test_data, f)
        
        # Load the conversation
        self.manager.load_conversation(filepath)
        
        # Verify loaded data
        self.assertEqual(self.manager.conversation_id, "test_conv_123")
        self.assertEqual(self.manager.model, "gpt-4o")
        self.assertEqual(self.manager.tools, ["file_search"])
        self.assertEqual(self.manager.metadata["test"], "value")
        self.assertEqual(len(self.manager.messages), 1)
        self.assertEqual(self.manager.messages[0]["content"], "Test message")
    
    def test_load_conversation_defaults_to_gpt5(self):
        """Test that loading a conversation without model defaults to GPT-5."""
        test_data = {
            "conversation_id": "test_conv_456",
            "messages": []
        }
        
        filepath = os.path.join(self.temp_dir, "test_default.json")
        with open(filepath, 'w') as f:
            json.dump(test_data, f)
        
        self.manager.load_conversation(filepath)
        
        # Should default to gpt-5
        self.assertEqual(self.manager.model, "gpt-5")
    
    def test_build_context(self):
        """Test building context from conversation history."""
        self.manager.create_conversation()
        
        # Add messages
        self.manager.messages.append({"role": "user", "content": "Hello"})
        self.manager.messages.append({"role": "assistant", "content": "Hi there"})
        self.manager.messages.append({"role": "user", "content": "How are you?"})
        
        context = self.manager._build_context()
        
        self.assertIsNotNone(context)
        self.assertIn("user: Hello", context)
        self.assertIn("assistant: Hi there", context)
        # The last message should not be in context (it's excluded)
        self.assertNotIn("How are you?", context)


class TestConversationManagerIntegration(unittest.TestCase):
    """Integration tests that may require API access (optional)."""
    
    @unittest.skipUnless(os.getenv("OPENAI_API_KEY"), "Requires OPENAI_API_KEY")
    def test_real_api_call(self):
        """Test a real API call (requires valid API key)."""
        manager = ConversationManager()
        manager.create_conversation(model="gpt-4o")  # Use gpt-4o for testing
        
        try:
            response = manager.send_message("Say 'test successful' and nothing else.")
            self.assertTrue(response.get("success", False))
            self.assertIsNotNone(response.get("content"))
            print(f"\nReal API Response: {response.get('content')}")
        except Exception as e:
            self.skipTest(f"API call failed: {e}")


def run_tests(verbose=True):
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestConversationManager))
    suite.addTests(loader.loadTestsFromTestCase(TestConversationManagerIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    print("=" * 70)
    print("Testing ConversationManager")
    print("=" * 70)
    
    # Run tests
    result = run_tests(verbose=True)
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
