"""
Day 1: Resume PDF -> interview questions (JSON)

Setup (terminal):
    pip install pypdf google-genai python-dotenv
    .env file mein GEMINI_API_KEY=your_key likho

Run:
    python day1_question_generator.py resume.pdf
"""
import json
import os
import sys

from google import genai
from google.genai import types
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()  # .env file se GEMINI_API_KEY load karta hai

# Model name badalta rehta hai. Google AI Studio mein dekho kaun sa free model available hai.
MODEL = "gemini-3.8-flash"


def read_resume(path: str) -> str:
    """PDF ke saare pages ka text nikalta hai."""
    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(pages).strip()
    if not text:
        raise ValueError("PDF se text nahi nikla. Shayad scanned PDF hai.")
    return text


def build_prompt(resume_text: str) -> str:
    return f"""You are a technical interviewer.
Read the resume below and create interview questions based ONLY on the
projects, skills and experience mentioned in it.

Return JSON in exactly this format:
{{
  "questions": [
    {{"type": "technical", "difficulty": "easy|medium|hard", "question": "..."}}
  ]
}}
Give 5 technical questions and 2 behavioral questions.

RESUME:
{resume_text}
"""


def generate_questions(resume_text: str, retries: int = 2) -> list:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    config = types.GenerateContentConfig(response_mime_type="application/json")

    for attempt in range(retries + 1):
        response = client.models.generate_content(
            model=MODEL, contents=build_prompt(resume_text), config=config
        )
        try:
            data = json.loads(response.text)
            questions = data["questions"]
            # Validation: har question mein zaruri keys honi chahiye
            if all("question" in q and "type" in q for q in questions):
                return questions
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
        print(f"Galat JSON aaya, dobara try ({attempt + 1})...")

    raise RuntimeError("Valid questions nahi mile.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python day1_question_generator.py resume.pdf")
        sys.exit(1)

    text = read_resume(sys.argv[1])
    for i, q in enumerate(generate_questions(text), 1):
        print(f"{i}. [{q['type']}] {q['question']}")
