import sys
import os
sys.path.append(os.getcwd())
from TinyTroupe.protocol import Message
from TinyTroupe.agent import TinyPerson
from TinyTroupe.environment import TinyWorld

def test_protocol():
    print("Testing A2A Protocol...")
    
    # 1. Test Message Creation
    msg = Message(sender="Alice", content="Hello World", type="text")
    print(f"Created Message: {msg.to_string()}")
    assert msg.sender == "Alice"
    assert msg.content == "Hello World"
    
    # 2. Test Agent Sending Message
    agent = TinyPerson("Bob")
    # Mocking act to return a Message (since we can't easily mock Gemini here without cost)
    # We'll just check if listen accepts a Message
    
    print("Testing Agent Listen...")
    agent.listen(msg)
    memory = agent.episodic_memory.retrieve_all()
    print(f"Agent Memory: {memory}")
    assert any("Heard [Alice]: Hello World" in str(m) for m in memory)
    
    print("SUCCESS: Protocol verified.")

if __name__ == "__main__":
    test_protocol()
