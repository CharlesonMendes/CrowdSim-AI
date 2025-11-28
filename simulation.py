import asyncio
import json
import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Ensure current directory is in sys.path for local imports
sys.path.append(os.getcwd())
print(f"DEBUG: sys.path: {sys.path}")
print(f"DEBUG: CWD: {os.getcwd()}")
print(f"DEBUG: tinytroupe exists: {os.path.exists('tinytroupe')}")
print(f"DEBUG: tinytroupe/__init__.py exists: {os.path.exists('tinytroupe/__init__.py')}")

# Check for API keys
if not os.getenv("GEMINI_API_KEY"):
    print("WARNING: GEMINI_API_KEY not found in .env.")
    print("TinyTroupe requires an LLM to function.")
    # We'll proceed, but it might fail if not configured globally elsewhere.

try:
    from TinyTroupe.agent import TinyPerson
    from TinyTroupe.environment import TinyWorld
    from TinyTroupe.factory import TinyPersonFactory
    import TinyTroupe.utils as utils
    from TinyTroupe.utils import generate_content_with_retry
except ImportError as e:
    print(f"Error: TinyTroupe not found or import failed. Details: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp_server import web_search, get_sentiment # Import local tools
from session_manager import SessionManager
from observability import StructuredLogger, Metrics
from evaluator import Evaluator

# ... (imports remain the same)

async def analyze_responses(responses, question):
    """Analyzes sentiment of agent responses using Gemini."""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-lite-preview-02-05')
        prompt = f"""
        Analyze the sentiment of the following focus group responses to the question: "{question}"
        
        Responses:
        {responses}
        """
        
        # Expect JSON output
        prompt += "\nProvide the output as a valid JSON object with keys: 'score' (1-10), 'label', 'summary'."
        
        response_obj = generate_content_with_retry(model, prompt)
        text = response_obj.text.strip()
        
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
            
        return json.loads(text)
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return {"score": 5, "label": "Neutral", "summary": "Error analyzing sentiment."}

async def run_simulation(questions, additional_context="", num_agents=5, min_age=19, max_age=60, session_id=None):
    print("Starting CrowdSim AI...")
    
    session_manager = SessionManager()
    if not session_id:
        session_id = session_manager.create_session_id()
        print(f"Created New Session ID: {session_id}")
        is_new_session = True
    else:
        print(f"Resuming Session ID: {session_id}")
        is_new_session = False

    # Initialize Observability
    logger = StructuredLogger()
    metrics = Metrics()
    evaluator = Evaluator()
    
    logger.log("simulation_start", {"session_id": session_id, "num_agents": num_agents})

    # Ensure questions is a list
    if isinstance(questions, str):
        questions = [questions]

    agents = []
    if is_new_session:
        # 1. Load Personas (Standard Creation)
        try:
            with open("personas.json", "r") as f:
                personas_data = json.load(f)
        except FileNotFoundError:
            print("Error: personas.json not found.")
            return {"error": "personas.json not found"}

        # Filter by age
        filtered_personas = [
            p for p in personas_data 
            if min_age <= p["age"] <= max_age
        ]

        if not filtered_personas:
            return {"error": f"No agents found in age range {min_age}-{max_age}."}

        # Select agents
        import random
        if len(filtered_personas) > num_agents:
            selected_personas = random.sample(filtered_personas, num_agents)
        else:
            selected_personas = filtered_personas

        for p_data in selected_personas:
            agent = TinyPerson(p_data["name"])
            agent.define("age", p_data["age"])
            agent.define("occupation", p_data["occupation"])
            agent.define("personality", p_data["personality"])
            agent.define("interests", p_data["interests"])
            
            # Register Tools
            agent.add_tool("web_search", web_search, "Performs a web search using DuckDuckGo. Use this tool when you need to find real-time information, news, or product details.")
            
            agents.append(agent)
            print(f"Created agent: {p_data['name']} ({p_data['age']})")
    else:
        # Load agents from session
        try:
            agents, _ = session_manager.load_session(session_id)
            print(f"Loaded {len(agents)} agents from session.")
            # Re-register tools (functions aren't pickled)
            for agent in agents:
                 agent.add_tool("web_search", web_search, "Performs a web search using DuckDuckGo. Use this tool when you need to find real-time information, news, or product details.")
        except Exception as e:
            return {"error": f"Failed to load session: {e}"}

    # 2. Create World
    world = TinyWorld("CrowdSimAI_Room", agents)
    world.make_everyone_accessible()

    # Broadcast Context first
    if additional_context:
        print(f"\nBroadcast Context: {additional_context}")
        world.broadcast(f"Context for this session: {additional_context}")

    results_data = {
        "overall_sentiment": 0,
        "question_details": [],
        "agents": [a.name for a in agents],
        "full_logs": "",
        "quality_metrics": {}
    }

    total_score = 0
    total_quality = {"relevance": 0, "coherence": 0, "fidelity": 0}
    response_count = 0
    full_conversation_log = ""

    # 3. Interaction Loop per Question
    import time
    for i, question in enumerate(questions):
        # Rate limiting: Pause between questions to reset quota window
        if i > 0:
            print("Pausing for 10 seconds to respect API rate limits...")
            time.sleep(10)

        print(f"\n--- Processing Question {i+1}: {question} ---")
        world.broadcast(f"Question {i+1}: {question}")
        
        # Run for 1 turn (everyone responds once)
        actions = world.run(1)
        
        # Collect responses for this turn
        current_responses = ""
        for agent_name, action in actions:
            current_responses += f"{agent_name}: {action}\n"
            
            # Log Action
            logger.log("agent_action", {"agent": agent_name, "action": action, "question": question})
            
            # Evaluate Response (LLM-as-a-Judge)
            # Find the agent object to get persona details
            agent_obj = next((a for a in agents if a.name == agent_name), None)
            if agent_obj:
                persona_desc = f"{agent_obj.attributes.get('age')} year old {agent_obj.attributes.get('occupation')}, {agent_obj.attributes.get('personality')}"
                eval_score = await evaluator.evaluate_response(question, action, persona_desc)
                
                logger.log("agent_evaluation", {"agent": agent_name, "scores": eval_score})
                
                total_quality["relevance"] += eval_score.get("relevance", 0)
                total_quality["coherence"] += eval_score.get("coherence", 0)
                total_quality["fidelity"] += eval_score.get("fidelity", 0)
                response_count += 1
        
        full_conversation_log += f"\n### Question {i+1}: {question}\n{current_responses}\n"

        # Analyze Sentiment for this question
        analysis = await analyze_responses(current_responses, question)
        print(f"Analysis: {analysis}")
        
        results_data["question_details"].append({
            "question": question,
            "score": analysis.get("score", 5),
            "label": analysis.get("label", "Neutral"),
            "summary": analysis.get("summary", ""),
            "responses": current_responses
        })
        total_score += analysis.get("score", 5)

    # 4. Finalize Results
    if questions:
        results_data["overall_sentiment"] = round(total_score / len(questions), 1)
        
    if response_count > 0:
        results_data["quality_metrics"] = {
            "relevance": round(total_quality["relevance"] / response_count, 1),
            "coherence": round(total_quality["coherence"] / response_count, 1),
            "fidelity": round(total_quality["fidelity"] / response_count, 1)
        }
    
    results_data["full_logs"] = full_conversation_log
    
    # Generate Report Text
    report = f"""# Focus Group Report

## Overall Sentiment Score: {results_data['overall_sentiment']}/10

## Participant Demographics
{', '.join([f"{a.name} ({a.attributes['age']})" for a in agents])}

## Detailed Analysis
"""
    for qd in results_data["question_details"]:
        report += f"\n### Q: {qd['question']}\n"
        report += f"**Sentiment:** {qd['score']}/10 ({qd['label']})\n"
        report += f"**Summary:** {qd['summary']}\n"
    
    report += f"\n## Conversation Logs\n{full_conversation_log}"
    
    results_data["report"] = report
    results_data["session_id"] = session_id
    
    # Save Session
    session_manager.save_session(session_id, agents)
    
    return results_data

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--session_id", type=str, help="Session ID to resume")
    args = parser.parse_args()
    
    default_stimulus = "What do you think of this $1000 smart toaster?"
    asyncio.run(run_simulation(default_stimulus, session_id=args.session_id))
