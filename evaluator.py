import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
from TinyTroupe.utils import generate_content_with_retry

load_dotenv()

class Evaluator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-lite-preview-02-05')
        else:
            print("WARNING: GEMINI_API_KEY not found for Evaluator.")
            self.model = None

    async def evaluate_response(self, question, response, persona):
        """
        Evaluates an agent's response based on Relevance, Coherence, and Persona Fidelity.
        """
        if not self.model:
            return {"relevance": 0, "coherence": 0, "fidelity": 0}

        prompt = f"""
        You are an expert judge evaluating an AI agent's response in a focus group simulation.
        
        Context:
        - Question: "{question}"
        - Agent Persona: {persona}
        - Agent Response: "{response}"
        
        Evaluate the response on a scale of 1-5 for the following criteria:
        1. Relevance: Does the answer directly address the question?
        2. Coherence: Is the response logical, grammatical, and easy to understand?
        3. Fidelity: Does the response sound like it came from the described persona?
        
        Provide the output as a valid JSON object with keys: "relevance", "coherence", "fidelity".
        Do not include markdown formatting.
        """
        
        try:
            result = generate_content_with_retry(self.model, prompt)
            text = result.text.strip()
            if text.startswith("```json"):
                text = text[7:-3]
            elif text.startswith("```"):
                text = text[3:-3]
            
            scores = json.loads(text)
            return scores
        except Exception as e:
            print(f"Evaluation failed: {e}")
            return {"relevance": 3, "coherence": 3, "fidelity": 3} # Default fallback
