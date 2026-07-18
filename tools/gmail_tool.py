from dataclasses import dataclass


@dataclass
class Email:
    id: str
    sender: str
    subject: str
    body: str


DEMO_EMAILS = [
    Email(
        id="demo-001",
        sender="sarah.jones@acmewidgets.com",
        subject="Question about invoice #4412",
        body="Hi, I noticed invoice #4412 charges $450 but I thought our agreed rate was $400/month. Could you clarify before I process payment? Thanks, Sarah",
    ),
    Email(
        id="demo-002",
        sender="newclient@brightstart.io",
        subject="Interested in your consulting services",
        body="Hello, I found your site through a referral. We're a 12-person startup looking for ongoing marketing consulting, roughly 10 hours/month. What are your rates and availability? Best, Devon",
    ),
    Email(
        id="demo-003",
        sender="promo@totallynotspam.biz",
        subject="You've won a FREE cruise!!!",
        body="Click here now to claim your prize before it expires!!!",
    ),
]


def fetch_unread_emails(max_results: int = 10) -> list[Email]:
    return DEMO_EMAILS[:max_results]