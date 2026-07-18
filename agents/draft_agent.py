from memory.memory_store import get_past_interactions
import os
from dotenv import load_dotenv
from google import genai
from tools.sheets_tool import get_client_record
from langsmith import traceable

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def load_company_info() -> str:
    with open("docs/company_info.txt", "r") as f:
        return f.read()

@traceable(name="draft_reply")
def draft_reply(sender: str, subject: str, body: str, classification: str) -> str:
    company_info = load_company_info()
    client_record = get_client_record(sender)

    if client_record:
        client_context = (
            f"This sender IS an existing client in our CRM. Their record:\n"
            f"Name: {client_record['name'].strip()}\n"
            f"Status: {client_record['status']}\n"
            f"Current rate: ${client_record['monthly_rate']}/month\n"
            f"Notes: {client_record['notes']}"
        )
    else:
        client_context = "This sender is NOT in our CRM (likely a new prospect)."

    prompt = f"""You are drafting an email reply on behalf of Bright Consulting.

COMPANY CONTEXT:
{company_info}

CLIENT RECORD:
{client_context}

INCOMING EMAIL (classified as: {classification}):
From: {sender}
Subject: {subject}
{body}

Write a warm, professional reply using ONLY the facts in the company context and
client record above. Do not invent any details not explicitly stated. If the client
record answers the question directly, use it confidently instead of asking the sender
to confirm something you already know.
Keep it under 120 words. Sign off as "The Bright Consulting Team"."""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
    )
    return response.text.strip()


if __name__ == "__main__":
    draft = draft_reply(
        sender="sarah.jones@acmewidgets.com",
        subject="Question about invoice #4412",
        body="Hi, I noticed invoice #4412 charges $450 but I thought our rate was $400/month.",
        classification="billing_question",
    )
    print(draft)