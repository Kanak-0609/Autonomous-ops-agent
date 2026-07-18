"""
Human-in-the-loop approval gate. Before any drafted action (sending an email,
updating a client status) actually executes, this pauses and asks for
explicit yes/no confirmation.

This terminal version is for local development. Week 3 later swaps this
same interface for a Slack-based approval flow without changing the
agents that call it.
"""


def request_approval(action_description: str, details: str) -> bool:
    print("\n" + "=" * 60)
    print("APPROVAL REQUIRED")
    print("=" * 60)
    print(f"Action: {action_description}")
    print("-" * 60)
    print(details)
    print("=" * 60)

    while True:
        response = input("Approve this action? (y/n): ").strip().lower()
        if response in ("y", "yes"):
            print("Approved.\n")
            return True
        if response in ("n", "no"):
            print("Rejected.\n")
            return False
        print("Please type 'y' or 'n'.")


if __name__ == "__main__":
    result = request_approval(
        action_description="Send email reply to sarah.jones@acmewidgets.com",
        details="Subject: Re: Question about invoice #4412\n\nHi Sarah, ...",
    )
    print("Result:", result)