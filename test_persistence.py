import sys
import os
import json
sys.path.append(os.getcwd())
from TinyTroupe.agent import TinyPerson
from session_manager import SessionManager

def test_persistence():
    print("Testing Persistence...")
    
    # 1. Create Agent and add memory
    agent = TinyPerson("MemoryTester")
    agent.define("age", 25)
    agent.listen("The secret code is 12345.")
    
    # 2. Save Session
    manager = SessionManager()
    session_id = "test_session_123"
    manager.save_session(session_id, [agent])
    
    # 3. Load Session
    loaded_agents, _ = manager.load_session(session_id)
    loaded_agent = loaded_agents[0]
    
    # 4. Verify Memory
    memories = loaded_agent.episodic_memory.retrieve_all()
    print(f"Loaded Memories: {memories}")
    
    if any("12345" in str(m) for m in memories):
        print("SUCCESS: Agent remembered the secret code.")
    else:
        print("FAILURE: Agent forgot the secret code.")

if __name__ == "__main__":
    test_persistence()
