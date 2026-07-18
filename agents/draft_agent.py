import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def load_company_info() -> str:
    with open("docs/company_info.txt", "r") as f:
        return f.read()


def draft_reply(sender: str, subject: str, body: str, classification: str) -> str:
    company_info = load_company_info()

    prompt = f"""You are drafting an email reply on behalf of Bright Consulting.

COMPANY CONTEXT:
{company_info}

INCOMING EMAIL (classified as: {classification}):
From: {sender}
Subject: {subject}
{body}

Write a warm, professional reply using ONLY the facts in the company context above.
Do not invent any details not explicitly stated — this includes the client's billing
history, how long they've been a client, what phase of onboarding they are in, or any
other specifics not present in the company context or the incoming email itself.
If the incoming email doesn't give you enough information to answer precisely, ask
a clarifying question instead of guessing.
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