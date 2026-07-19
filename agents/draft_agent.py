import os
from dotenv import load_dotenv
from google import genai
from langsmith import traceable
from tools.sheets_tool import get_client_record
from memory.memory_store import get_past_interactions, get_company_config

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def _format_company_context(config: dict) -> str:
    return (
        f"Services: {config['services']}\n"
        f"Standard rate: {config['standard_rate']}\n"
        f"Onboarding rate: {config['onboarding_rate']}\n"
        f"Availability: {config['availability']}\n"
        f"Response policy: {config['response_policy']}"
    )


@traceable(name="draft_reply")
def draft_reply(organization_id: int, sender: str, subject: str, body: str, classification: str) -> str:
    config = get_company_config(organization_id)
    if config is None:
        raise ValueError(
            f"No company_config found for organization_id={organization_id}. "
            "Run python -m memory.memory_store to seed a default organization, "
            "or create one for this tenant first."
        )
    company_info = _format_company_context(config)

    client_record = get_client_record(sender)
    past_interactions = get_past_interactions(organization_id, sender)

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

    if past_interactions:
        history_lines = [
            f"- {i['subject']} ({i['classification']}): {i['summary']}"
            for i in past_interactions
        ]
        history_context = "Past interactions with this sender:\n" + "\n".join(history_lines)
    else:
        history_context = "No past interactions with this sender."

    prompt = f"""You are drafting an email reply on behalf of this business.

COMPANY CONTEXT:
{company_info}

CLIENT RECORD:
{client_context}

PAST INTERACTION HISTORY:
{history_context}

INCOMING EMAIL (classified as: {classification}):
From: {sender}
Subject: {subject}
{body}

Write a warm, professional reply using ONLY the facts in the company context, client
record, and past interaction history above. Do not invent any details not explicitly
stated. If this topic was already addressed in a past interaction, acknowledge that
naturally rather than explaining everything from scratch again.
Keep it under 120 words. Sign off as "The Team"."""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
    )
    return response.text.strip()


if __name__ == "__main__":
    draft = draft_reply(
        organization_id=1,
        sender="sarah.jones@acmewidgets.com",
        subject="Question about invoice #4412",
        body="Hi, I noticed invoice #4412 charges $450 but I thought our rate was $400/month.",
        classification="billing_question",
    )
    print(draft)