from tools.gmail_tool import fetch_unread_emails
from agents.triage_agent import triage_email
from agents.draft_agent import draft_reply


def run():
    emails = fetch_unread_emails()
    print(f"Fetched {len(emails)} unread email(s).\n")

    for email in emails:
        triage_result = triage_email(email.sender, email.subject, email.body)
        print(f"[{triage_result.classification.upper():17s}] conf={triage_result.confidence:.2f}  {email.subject!r}")
        print(f"   Reasoning: {triage_result.reasoning}")

        if triage_result.classification == "spam":
            print("   -> Skipping draft (spam).\n")
            continue

        draft = draft_reply(
            sender=email.sender,
            subject=email.subject,
            body=email.body,
            classification=triage_result.classification,
        )
        print(f"   -> Drafted reply:\n")
        print("   " + draft.replace("\n", "\n   "))
        print()


if __name__ == "__main__":
    run()