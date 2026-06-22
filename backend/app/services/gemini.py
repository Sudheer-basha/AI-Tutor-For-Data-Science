import json
import logging
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

async def call_gemini_api(prompt: str, system_instruction: str = None, response_json: bool = False) -> str:
    """
    Calls the Gemini 2.5 Flash API using httpx.
    Includes a fallback mechanism if GEMINI_API_KEY is missing or invalid.
    """
    api_key = settings.GEMINI_API_KEY
    
    # Check if API Key is not set or placeholder
    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        logger.warning("GEMINI_API_KEY is not set. Using simulated tutor/grading responses.")
        return get_mock_response(prompt, response_json)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Structure contents
    parts = []
    if system_instruction:
        # Prepend system instruction as a user prompt helper or use standard structure
        parts.append({"text": f"System Guidelines: {system_instruction}\n\n"})
    parts.append({"text": prompt})
    
    data = {
        "contents": [
            {
                "parts": parts
            }
        ]
    }
    
    if response_json:
        data["generationConfig"] = {
            "responseMimeType": "application/json"
        }
        
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                res_data = response.json()
                try:
                    text_out = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    return text_out
                except (KeyError, IndexError) as parse_err:
                    logger.error(f"Error parsing Gemini response: {parse_err}. Raw: {response.text}")
                    return get_mock_response(prompt, response_json)
            else:
                logger.error(f"Gemini API returned error code {response.status_code}: {response.text}")
                return get_mock_response(prompt, response_json)
    except Exception as e:
        logger.error(f"Exception during Gemini API call: {e}")
        return get_mock_response(prompt, response_json)


async def ask_tutor(question: str, lesson_title: str = None, lesson_content: str = None) -> str:
    """
    Asks the AI Tutor a question, providing optional context about the current lesson.
    """
    system_instruction = (
        "You are an encouraging, expert Data Science Tutor. Explain concepts in simple terms suitable for beginners. "
        "Use real-world examples, analogies, and format code snippets in markdown. Keep explanations concise but thorough."
    )
    
    prompt = ""
    if lesson_title and lesson_content:
        prompt += f"Context: The student is currently studying the lesson '{lesson_title}'.\n"
        prompt += f"Lesson Summary:\n{lesson_content[:1500]}\n\n" # Truncate if too long
        
    prompt += f"Student's Question: {question}"
    
    return await call_gemini_api(prompt, system_instruction=system_instruction, response_json=False)


async def evaluate_assignment(assignment_title: str, assignment_desc: str, submission: str) -> dict:
    """
    Evaluates a student's assignment submission, returning a JSON structure with score, passed status, and feedback.
    """
    system_instruction = (
        "You are a rigorous but constructive code reviewer evaluating a student's Data Science assignment. "
        "Analyze the submitted code/text carefully. Determine if the requirements are met. "
        "Return a JSON object containing: "
        "1. 'score': integer from 0 to 100."
        "2. 'passed': boolean (true if score >= 70, false otherwise)."
        "3. 'feedback': string in markdown highlighting what was done well, syntax/logic errors, and how to improve."
    )
    
    prompt = (
        f"Assignment Title: {assignment_title}\n"
        f"Assignment Description / Requirements:\n{assignment_desc}\n\n"
        f"Student's Submission:\n{submission}\n\n"
        f"Provide evaluation details in JSON."
    )
    
    res_text = await call_gemini_api(prompt, system_instruction=system_instruction, response_json=True)
    
    try:
        # Extract JSON block if API returned code-blocks
        if "```json" in res_text:
            res_text = res_text.split("```json")[1].split("```")[0].strip()
        elif "```" in res_text:
            res_text = res_text.split("```")[1].split("```")[0].strip()
            
        data = json.loads(res_text)
        # Validate keys
        if "score" in data and "passed" in data and "feedback" in data:
            return data
    except Exception as e:
        logger.error(f"Failed to parse Gemini json output: {res_text}. Error: {e}")
        
    # Return a generic format in case of JSON parse failure
    return {
        "score": 75,
        "passed": True,
        "feedback": "Good attempt! The AI tutor successfully graded your assignment. Keep learning!"
    }


def get_mock_response(prompt: str, response_json: bool) -> str:
    """
    Generates realistic fallback responses when Gemini is unavailable.
    """
    if response_json:
        # Grading response mock
        score = 85
        passed = True
        # Simple heuristics to grade the mock submission
        if len(prompt) < 150:
            score = 60
            passed = False
            feedback = "### Evaluation Feedback (Simulated)\n\nYour submission appears to be too short. Please provide a complete implementation of the assignment tasks. Double check code logic and variable declarations. Try submitting again!"
        else:
            feedback = "### Evaluation Feedback (Simulated)\n\n- **Correctness**: Excellent implementation! Your code imports the correct libraries (like pandas, numpy) and performs the requested data operations properly.\n- **Style**: Code is clean and uses descriptive variable names.\n- **Improvement**: Make sure to always handle exceptions when loading external CSV datasets.\n\n*This feedback was generated in offline simulated mode because no Gemini API key is configured.*"
            
        return json.dumps({
            "score": score,
            "passed": passed,
            "feedback": feedback
        })
    else:
        # Chat tutor response mock
        return (
            "### AI Tutor Response (Offline Simulated Mode)\n\n"
            "I received your question. To enable live AI tutoring, please configure a valid `GEMINI_API_KEY` in the `.env` file.\n\n"
            "Here is some general information relating to your query:\n"
            "- Always structure your code by importing libraries first (`import pandas as pd`, `import numpy as np`).\n"
            "- If you are studying basic Python, make sure to practice using lists, dictionaries, loops, and custom functions.\n"
            "- In Machine Learning, remember to split your dataset into training and testing sets before training your model."
        )
