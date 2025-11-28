import asyncio
import sys
import os
sys.path.append(os.getcwd())
from evaluator import Evaluator

async def test_evaluation():
    print("Testing Evaluator...")
    evaluator = Evaluator()
    
    question = "What do you think about electric cars?"
    
    # Test Case 1: Good Response
    response_good = "I think they are great for the environment, though charging infrastructure needs work."
    persona_good = "30 year old Environmentalist, passionate about sustainability"
    
    print(f"\nEvaluating Good Response:\nQ: {question}\nA: {response_good}\nP: {persona_good}")
    score_good = await evaluator.evaluate_response(question, response_good, persona_good)
    print(f"Scores: {score_good}")
    
    # Test Case 2: Bad Response (Irrelevant)
    response_bad = "I like pizza."
    persona_bad = "30 year old Environmentalist"
    
    print(f"\nEvaluating Bad Response:\nQ: {question}\nA: {response_bad}\nP: {persona_bad}")
    score_bad = await evaluator.evaluate_response(question, response_bad, persona_bad)
    print(f"Scores: {score_bad}")

if __name__ == "__main__":
    asyncio.run(test_evaluation())
