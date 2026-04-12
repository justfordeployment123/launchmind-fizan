"""Marketing Agent - Generates copy, sends mock email, posts to Slack."""
import json
import os
import re
from base_agent import BaseAgent


class MarketingAgent(BaseAgent):
    """Generates marketing copy, sends email (mock), posts to Slack (real)."""

    def __init__(self):
        super().__init__("marketing")
        self.slack_token = os.environ.get("SLACK_BOT_TOKEN", "")
        self.from_email = os.environ.get("SENDGRID_FROM_EMAIL", "agent@launchmind.ai")
        self.to_email = os.environ.get("SENDGRID_TO_EMAIL", "test@example.com")

    # ── public entry point ───────────────────────────────────────────────
    def run(self, product_spec: dict, pr_url: str = "") -> dict:
        """Generate copy, send email, post to Slack. Returns result dict."""

        copy = self._generate_copy(product_spec)
        email_sent = self._send_email(copy)
        slack_posted = self.post_to_slack(
            tagline=copy.get("tagline", "Amazing Product"),
            description=copy.get("description", "Check out our product"),
            pr_url=pr_url,
        )

        return {
            "tagline": copy.get("tagline"),
            "description": copy.get("description"),
            "email_sent": email_sent,
            "slack_posted": slack_posted,
            "pr_url": pr_url,
            "copy": copy,
        }

    # ── LLM: generate marketing copy ────────────────────────────────────
    def _generate_copy(self, spec: dict) -> dict:
        print(f"   📢 Marketing: generating copy via LLM...")

        system_prompt = (
            "You are a growth marketer. Generate marketing copy in JSON. Keys:\n"
            "- tagline (string, under 10 words)\n"
            "- description (string, 2-3 sentences)\n"
            "- cold_email_subject (string)\n"
            "- cold_email_body (string, 4-6 sentences)\n"
            "- social_twitter (string, tweet)\n"
            "- social_linkedin (string, post)\n"
            "- social_instagram (string, caption)\n"
            "Return ONLY valid JSON."
        )
        user_prompt = (
            f"Product: {spec.get('value_proposition', 'An amazing product')}\n"
            f"Features: {json.dumps([f['name'] for f in spec.get('features', [])[:3]])}\n"
            f"Target users: {json.dumps([p.get('role','') for p in spec.get('personas', [])])}"
        )

        raw = self.call_llm(system_prompt, user_prompt)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group())
                except json.JSONDecodeError:
                    pass
        return {
            "tagline": "Test smarter, ship faster",
            "description": "AutoTest uses AI to generate comprehensive test cases from your Python docstrings. Save hours on testing, catch more bugs, ship with confidence.",
            "cold_email_subject": "Generate tests 10x faster with AutoTest",
            "cold_email_body": "Hi there,\n\nWe built AutoTest to solve a problem every Python dev faces: writing comprehensive tests is tedious. AutoTest reads your docstrings and generates pytest-compatible tests automatically — covering edge cases you'd miss. Try it free today.\n\nBest,\nThe LaunchMind Team",
            "social_twitter": "Tired of writing tests? AutoTest generates them from your docstrings. Ship faster.",
            "social_linkedin": "Excited to launch AutoTest — an AI-powered testing tool for Python developers.",
            "social_instagram": "AutoTest: Less testing, more shipping.",
        }

    # ── Email (mock — prints to console) ─────────────────────────────────
    def _send_email(self, copy: dict) -> bool:
        subject = copy.get("cold_email_subject", "Check this out")
        body = copy.get("cold_email_body", "Hello!")

        print(f"\n   {'='*60}")
        print(f"   📨 EMAIL OUTPUT (Console Mock)")
        print(f"   {'='*60}")
        print(f"   TO      : {self.to_email}")
        print(f"   FROM    : {self.from_email}")
        print(f"   SUBJECT : {subject}")
        print(f"   {'─'*60}")
        for line in body.split("\n"):
            print(f"   {line}")
        print(f"   {'='*60}")
        print(f"   ✅ Email printed to console")
        return True

    # ── Slack (real — Block Kit) ─────────────────────────────────────────
    def post_to_slack(self, tagline: str, description: str, pr_url: str) -> bool:
        print(f"   💬 Marketing: posting to Slack #launches...")
        try:
            from slack_sdk import WebClient
            client = WebClient(token=self.slack_token)

            blocks = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": f"🚀 New Launch: {tagline}"},
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": description},
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*GitHub PR:*\n<{pr_url}|View PR>"},
                        {"type": "mrkdwn", "text": "*Status:*\nReady for review"},
                    ],
                },
            ]

            resp = client.chat_postMessage(channel="#launches", blocks=blocks)
            if resp.get("ok"):
                print(f"   ✅ Slack message posted to #launches")
                return True
            print(f"   ⚠️  Slack error: {resp.get('error')}")
        except Exception as e:
            print(f"   ❌ Slack error: {e}")
        return False
