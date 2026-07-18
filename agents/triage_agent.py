import os
import json
from dataclasses import dataclass
from typing import Literal
from langsmith import traceable

from dotenv import load_dotenv
from google import genai

load_dotenv()

Classification = Literal["billing_question", "new_inquiry", "spam", "other"]

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """You are a triage classifier for a small consulting business's inbox.
Classify the email into exactly one of these categories:
- billing_question: existing client asking about an invoice, payment, or rate
- new_inquiry: a prospective client asking about services, availability, or pricing
- spam: promotional, phishing, or irrelevant content
- other: anything that doesn't fit the above, such as scheduling requests, general
  check-ins, or internal admin -- do not force these into billing_question or
  new_inquiry just because the sender is a known client or prospect

Respond ONLY with valid JSON in this exact format, no other text:
{"classification": "<category>", "confidence": <0.0-1.0>, "reasoning": "<one sentence>"}
"""


@dataclass
class TriageResult:
    classification: Classification
    confidence: float
    reasoning: str


@traceable(name="triage_email")
def triage_email(sender: str, subject: str, body: str) -> TriageResult:
    user_content = f"From: {sender}\nSubject: {subject}\n\n{body}"

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=f"{SYSTEM_PROMPT}\n\n{user_content}",
    )

    text = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        parsed = json.loads(text)
        return TriageResult(
            classification=parsed["classification"],
            confidence=float(parsed["confidence"]),
            reasoning=parsed["reasoning"],
        )
    except (json.JSONDecodeError, KeyError) as e:
        return TriageResult(
            classification="new_inquiry",
            confidence=0.0,
            reasoning=f"Failed to parse model output, flagging for manual review: {e}",
        )


if __name__ == "__main__":
    result = triage_email(
        sender="sarah.jones@acmewidgets.com",
        subject="Question about invoice #4412",
        body="Hi, I noticed invoice #4412 charges $450 but I thought our rate was $400/month.",
    )
    print(result)
