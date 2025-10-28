"""
Quick test to verify response extraction works correctly.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conversation_manager import ConversationManager

def test_response_extraction():
    """Test that we can extract content from actual API responses."""
    print("Testing response extraction...")
    
    # Check if API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set, skipping live test")
        return
    
    try:
        # Create a conversation manager
        manager = ConversationManager()
        manager.create_conversation(model="gpt-4o")  # Use gpt-4o for testing
        
        print("Sending test message...")
        response = manager.send_message("Say 'Hello World' and nothing else.")
        
        print(f"\n✅ Success!")
        print(f"Response type: {type(response)}")
        print(f"Response keys: {response.keys()}")
        print(f"Success flag: {response.get('success')}")
        print(f"Content: {response.get('content')}")
        print(f"Message count: {response.get('message_count')}")
        
        # Verify response is JSON serializable
        import json
        json_str = json.dumps(response)
        print(f"\n✅ Response is JSON serializable")
        print(f"JSON length: {len(json_str)} characters")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_response_extraction()
    sys.exit(0 if success else 1)
