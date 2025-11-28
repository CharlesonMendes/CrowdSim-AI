import sys
import os
sys.path.append(os.getcwd())
from TinyTroupe.agent import TinyPerson
from mcp_server import web_search

def test_tool_usage():
    print("Testing Tool Integration...")
    
    agent = TinyPerson("Tester")
    agent.add_tool("web_search", web_search, "Performs a web search. Use this to find information.")
    agent.define("age", 30)
    agent.define("occupation", "Tech Enthusiast")
    agent.define("personality", "Curious and data-driven")
    
    # Force a situation where search is needed
    question = "What is the current stock price of Apple (AAPL) today?"
    print(f"Asking agent: {question}")
    agent.listen(question)
    
    # The agent should decide to use the tool
    response = agent.act()
    print(f"Final Agent Response: {response}")
    
    # Check if tool was actually used (we can check memory)
    tool_used = any("Tool Result:" in str(m) for m in agent.episodic_memory.retrieve_all())
    if tool_used:
        print("SUCCESS: Agent used the tool.")
    else:
        print("WARNING: Agent did not use the tool (this might be due to LLM choice, but check logs).")

if __name__ == "__main__":
    test_tool_usage()
