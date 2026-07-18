"""
Hand-labeled test cases for the triage agent. Each entry has an email and
the classification a careful human would assign. Includes some genuinely
ambiguous cases on purpose -- a real eval suite should stress-test edge
cases, not just easy ones.
"""

TEST_CASES = [
    {
        "sender": "sarah.jones@acmewidgets.com",
        "subject": "Question about invoice #4412",
        "body": "Hi, I noticed invoice #4412 charges $450 but I thought our rate was $400/month.",
        "expected": "billing_question",
    },
    {
        "sender": "newclient@brightstart.io",
        "subject": "Interested in your consulting services",
        "body": "Hello, we're a 12-person startup looking for marketing consulting. What are your rates?",
        "expected": "new_inquiry",
    },
    {
        "sender": "promo@totallynotspam.biz",
        "subject": "You've won a FREE cruise!!!",
        "body": "Click here now to claim your prize before it expires!!!",
        "expected": "spam",
    },
    {
        "sender": "mike.chen@retailco.com",
        "subject": "Can we push back our monthly call?",
        "body": "Hi, could we move Thursday's check-in to Friday instead? Same time works.",
        "expected": "other",
    },
    {
        "sender": "sarah.jones@acmewidgets.com",
        "subject": "Thanks!",
        "body": "Just wanted to say thanks for the quick turnaround on last month's deliverables.",
        "expected": "other",
    },
    {
        "sender": "lisa@designstudio.co",
        "subject": "Wondering about your onboarding process",
        "body": "Hi there, before we sign anything, could you walk me through what the first month looks like?",
        "expected": "new_inquiry",
    },
    {
        "sender": "billing@acmewidgets.com",
        "subject": "Autopay failed for invoice #4390",
        "body": "Our card on file was declined for this month's payment. Can you resend the payment link?",
        "expected": "billing_question",
    },
    {
        "sender": "winner-notify@totally-legit-prizes.net",
        "subject": "URGENT: Verify your account now",
        "body": "Your account will be suspended unless you verify your details immediately. Click here.",
        "expected": "spam",
    },
    {
        "sender": "jordan@newventure.com",
        "subject": "Referred by a mutual friend",
        "body": "Hey! A friend mentioned you do brand consulting. We're pre-revenue but want to plan ahead. Available for a call?",
        "expected": "new_inquiry",
    },
    {
        "sender": "sarah.jones@acmewidgets.com",
        "subject": "Re: onboarding rate question",
        "body": "Thanks for clarifying last time -- one more question, does the $400 rate include social media management or is that extra?",
        "expected": "billing_question",  # tricky: sounds like a service question, but ties to rate/pricing
    },
    {
        "sender": "noreply@shippingupdates.xyz",
        "subject": "Your package could not be delivered",
        "body": "We attempted delivery but no one was home. Click to reschedule and confirm your address.",
        "expected": "spam",
    },
    {
        "sender": "devon@brightstart.io",
        "subject": "Following up on my last email",
        "body": "Just checking in -- did you get a chance to look at what I sent about our marketing needs?",
        "expected": "new_inquiry",
    },
    {
        "sender": "accounting@retailco.com",
        "subject": "Requesting updated W-9",
        "body": "For our records, could you send an updated W-9 form? Ours on file has expired.",
        "expected": "billing_question",
    },
    {
        "sender": "random123@freegiftcard-now.com",
        "subject": "Congratulations! Claim your $500 gift card",
        "body": "You've been selected! Complete this short survey to claim your reward.",
        "expected": "spam",
    },
    {
        "sender": "priya@growthlabs.io",
        "subject": "Quick question about capacity",
        "body": "Are you currently taking on new clients, or is your calendar full for now?",
        "expected": "new_inquiry",
    },
    {
        "sender": "tom.baker@acmewidgets.com",
        "subject": "Can you resend last month's receipt?",
        "body": "I need last month's paid invoice for our expense report. Could you send a copy?",
        "expected": "billing_question",
    },
]