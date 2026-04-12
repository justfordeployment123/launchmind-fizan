"""Marketing Agent - Generates marketing copy, sends email, posts to Slack."""
import json
import os
from base_agent import BaseAgent

class MarketingAgent(BaseAgent):
    """Marketing agent that creates marketing materials and sends communications."""

    def __init__(self):
        super().__init__("marketing")
        self.sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")
        self.slack_token = os.environ.get("SLACK_BOT_TOKEN")
        self.sendgrid_from = os.environ.get("SENDGRID_FROM_EMAIL")
        self.sendgrid_to = os.environ.get("SENDGRID_TO_EMAIL")

    def generate_marketing_copy(self, product_spec: dict) -> dict:
        """Use LLM to generate marketing copy."""
        print(f"\n📢 Marketing: Generating marketing copy...")

        system_prompt = """You are a growth marketer. Generate compelling marketing copy in JSON format.
Return a JSON object with these exact keys:
- tagline: string (under 10 words)
- description: string (2-3 sentences for landing page)
- cold_email_subject: string
- cold_email_body: string
- social_twitter: string (tweet about the product)
- social_linkedin: string (LinkedIn post)
- social_instagram: string (Instagram caption)"""

        value_prop = product_spec.get("value_proposition", "Amazing Product")
        features = product_spec.get("features", [])
        personas = product_spec.get("personas", [])

        user_prompt = f"""Generate marketing copy for this product:
Value Proposition: {value_prop}

Top Features:
{json.dumps([f['name'] for f in features[:3]], indent=2)}

Target Personas:
{json.dumps([p.get('role', '') for p in personas], indent=2)}

Create compelling, concise marketing copy. Return ONLY valid JSON."""

        response = self.call_llm(system_prompt, user_prompt)

        try:
            copy = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            copy = json.loads(json_match.group()) if json_match else self._default_copy()

        return copy

    def _default_copy(self) -> dict:
        """Fallback marketing copy."""
        return {
            "tagline": "Generate tests from docstrings in seconds",
            "description": "AutoTest uses AI to automatically generate comprehensive test cases from your Python docstrings. Save hours on testing, catch more bugs, ship faster.",
            "cold_email_subject": "Generate tests 10x faster with AutoTest",
            "cold_email_body": """Hi there,

We built AutoTest to solve a problem we faced: writing comprehensive test cases is tedious.

AutoTest reads your Python docstrings and generates pytest-compatible tests automatically.
- 70% faster test writing
- Better edge case coverage
- Integrates with your existing CI/CD

Get started free today.

Best,
LaunchMind Team""",
            "social_twitter": "🚀 Tired of writing tests? AutoTest generates them from your docstrings. 10x faster testing. Try free: [link]",
            "social_linkedin": "We're excited to launch AutoTest - the AI-powered testing tool for Python developers. Cut testing time by 70%. Check it out.",
            "social_instagram": "AutoTest: Less testing, more shipping ✨ #Startup #SoftwareDevelopment"
        }

    def send_email(self, subject: str, body: str) -> bool:
        """Send email (or mock by printing to console)."""
        print(f"\n📧 Marketing: Sending email...")

        # Mock email - just print to console
        print(f"\n{'='*70}")
        print(f"📨 EMAIL SENT (MOCK - Console Output)")
        print(f"{'='*70}")
        print(f"TO: {self.sendgrid_to}")
        print(f"FROM: {self.sendgrid_from}")
        print(f"SUBJECT: {subject}")
        print(f"{'='*70}")
        print(f"\n{body}")
        print(f"\n{'='*70}")
        print(f"✅ Email would be sent to: {self.sendgrid_to}")
        print(f"{'='*70}\n")

        return True

    def post_to_slack(self, tagline: str, description: str, pr_url: str) -> bool:
        """Post to Slack using Block Kit."""
        print(f"\n💬 Marketing: Posting to Slack...")

        try:
            from slack_sdk import WebClient

            client = WebClient(token=self.slack_token)

            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"🚀 New Launch: {tagline}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": description
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*GitHub PR:*\n<{pr_url}|View PR>"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Status:*\nReady for review"
                        }
                    ]
                }
            ]

            response = client.chat_postMessage(
                channel="#launches",
                blocks=blocks
            )

            if response["ok"]:
                print(f"✅ Slack message posted successfully")
                return True
            else:
                print(f"⚠️  Slack post failed: {response.get('error', 'Unknown error')}")
                return False

        except Exception as e:
            print(f"❌ Error posting to Slack: {str(e)}")
            return False

    def run(self):
        """Main marketing agent logic."""
        print(f"\n{'='*60}")
        print(f"📊 MARKETING AGENT STARTING")
        print(f"{'='*60}")

        product_spec = None
        pr_url = None

        # Wait for product spec and PR URL
        while True:
            messages = self.get_new_messages()
            for msg in messages:
                if msg.from_agent == "product" and msg.message_type == "task" and not product_spec:
                    product_spec = msg.payload
                    print(f"📋 Received product spec")

                if msg.from_agent == "ceo" and msg.message_type == "task":
                    if msg.payload.get("action") == "post_final_summary":
                        pr_url = msg.payload.get("engineer_output", {}).get("pr_url")
                        print(f"📌 Got PR URL and final summary task")

                if product_spec and pr_url:
                    break

            if product_spec and pr_url:
                break

        # Generate marketing copy
        copy = self.generate_marketing_copy(product_spec)

        # Send email
        email_sent = self.send_email(
            subject=copy.get("cold_email_subject", "New Product Launch"),
            body=copy.get("cold_email_body", "Check out our new product!")
        )

        # Post to Slack
        slack_posted = self.post_to_slack(
            tagline=copy.get("tagline", "Amazing Product"),
            description=copy.get("description", "Check out our new product"),
            pr_url=pr_url
        )

        # Send result back to CEO
        self.send_message(
            to_agent="ceo",
            message_type="result",
            payload={
                "tagline": copy.get("tagline"),
                "email_sent": email_sent,
                "slack_posted": slack_posted,
                "pr_url": pr_url,
                "copy": copy
            }
        )

        print(f"✅ Marketing work complete")
        print(f"   Email sent: {email_sent}")
        print(f"   Slack posted: {slack_posted}")
