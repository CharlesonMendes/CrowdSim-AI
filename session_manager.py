import os
import json
import uuid
from TinyTroupe.agent import TinyPerson

SESSION_DIR = "sessions"

class SessionManager:
    def __init__(self):
        if not os.path.exists(SESSION_DIR):
            os.makedirs(SESSION_DIR)

    def save_session(self, session_id, agents, world_state=None):
        """Saves the current session state to a JSON file."""
        data = {
            "session_id": session_id,
            "agents": [agent.to_dict() for agent in agents],
            "world_state": world_state or {}
        }
        
        filepath = os.path.join(SESSION_DIR, f"{session_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Session saved to {filepath}")

    def load_session(self, session_id):
        """Loads a session from a JSON file."""
        filepath = os.path.join(SESSION_DIR, f"{session_id}.json")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Session file {filepath} not found.")
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        agents = []
        for agent_data in data["agents"]:
            agents.append(TinyPerson.from_dict(agent_data))
            
        return agents, data.get("world_state", {})

    def list_sessions(self):
        """Lists all available session IDs."""
        if not os.path.exists(SESSION_DIR):
            return []
        return [f.replace(".json", "") for f in os.listdir(SESSION_DIR) if f.endswith(".json")]

    def create_session_id(self):
        return str(uuid.uuid4())
