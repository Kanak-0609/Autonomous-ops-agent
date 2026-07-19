from tools.gmail_tool import fetch_unread_emails
from agents.triage_agent import triage_email
from agents.draft_agent import draft_reply
from agents.approval_gate import request_approval
from memory.memory_store import init_db, log_interaction, get_or_create_organization

# For now this hardcodes the one tenant we've seeded. In a real multi-tenant
# deploy, this would come from which business's inbox is currently being
# processed (e.g. a queue job carrying organization_id, or a per-tenant
# scheduled run) rather than being fixed at the top of the file.
ORGANIZATION_NAME = "Bright Consulting"
ORGANIZATION_SLUG = "bright-consulting"


def run():
    init_db()
    organization_id = get_or_create_organization(ORGANIZATION_NAME, ORGANIZATION_SLUG)
    print(f"Running for organization: {ORGANIZATION_NAME} (id={organization_id})\n")

    emails = fetch_unread_emails()
    print(f"Fetched {len(emails)} unread email(s).\n")

    approved_count = 0
    rejected_count = 0
    skipped_count = 0

    for email in emails:
        triage_result = triage_email(email.sender, email.subject, email.body)
        print(f"[{triage_result.classification.upper():17s}] conf={triage_result.confidence:.2f}  {email.subject!r}")
        print(f"   Reasoning: {triage_result.reasoning}")

        if triage_result.classification in ("spam", "other"):
            print(f"   -> Skipping draft ({triage_result.classification}).\n")
            skipped_count += 1
            log_interaction(
                organization_id=organization_id,
                sender_email=email.sender,
                subject=email.subject,
                classification=triage_result.classification,
                outcome="skipped",
                summary=f"Not drafted: classified as {triage_result.classification}",
            )
            continue

        draft = draft_reply(
            organization_id=organization_id,
            sender=email.sender,
            subject=email.subject,
            body=email.body,
            classification=triage_result.classification,
        )

        approved = request_approval(
            action_description=f"Send email reply to {email.sender}",
            details=draft,
        )

        if approved:
            print(f"   -> [SENT] Reply to {email.sender}\n")
            approved_count += 1
            log_interaction(
                organization_id=organization_id,
                sender_email=email.sender,
                subject=email.subject,
                classification=triage_result.classification,
                outcome="sent",
                summary=draft[:200],
            )
        else:
            print(f"   -> [DISCARDED] Reply to {email.sender} was rejected\n")
            rejected_count += 1
            log_interaction(
                organization_id=organization_id,
                sender_email=email.sender,
                subject=email.subject,
                classification=triage_result.classification,
                outcome="rejected",
                summary=draft[:200],
            )

    print("--- Summary ---")
    print(f"Approved & sent: {approved_count}")
    print(f"Rejected: {rejected_count}")
    print(f"Skipped (spam/other): {skipped_count}")


if __name__ == "__main__":
    run()