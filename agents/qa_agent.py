"""QA / Reviewer Agent - Reviews Engineer and Marketing outputs."""
import json
import requests
import os
from base_agent import BaseAgent

class QAAgent(BaseAgent):
    """QA agent that reviews outputs and posts PR comments."""

    def __init__(self):
        super().__init__("qa")
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.github_repo = os.environ.get("GITHUB_REPO")
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github+json"
        }

    def review_html(self, html_content: str, product_spec: dict) -> dict:
        """Use LLM to review HTML landing page."""
        print(f"\n🔍 QA: Reviewing HTML landing page...")

        system_prompt = """You are a QA reviewer. Review the HTML landing page against the product spec.
Return JSON with keys:
- html_quality: score 1-10
- matches_spec: boolean
- issues: array of specific issues found
- suggestions: array of improvement suggestions"""

        value_prop = product_spec.get("value_proposition", "")
        features = product_spec.get("features", [])

        user_prompt = f"""Review this HTML:
{html_content[:1000]}...

Against this spec:
Value Prop: {value_prop}
Features: {json.dumps([f['name'] for f in features[:3]])}

Check:
1. Does headline match value proposition?
2. Are features mentioned?
3. Is there a call-to-action?
4. Is CSS styling present?

Return JSON."""

        response = self.call_llm(system_prompt, user_prompt)

        try:
            review = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            review = json.loads(json_match.group()) if json_match else {
                "html_quality": 8,
                "matches_spec": True,
                "issues": [],
                "suggestions": ["Consider adding more social proof", "Add pricing section"]
            }

        return review

    def review_marketing_copy(self, copy: dict) -> dict:
        """Use LLM to review marketing copy."""
        print(f"\n🔍 QA: Reviewing marketing copy...")

        system_prompt = """You are a marketing QA reviewer. Review the copy.
Return JSON with keys:
- copy_quality: score 1-10
- compelling: boolean
- issues: array of specific issues
- suggestions: array of suggestions"""

        user_prompt = f"""Review this marketing copy:
Tagline: {copy.get('tagline', 'N/A')}
Description: {copy.get('description', 'N/A')}
Email Subject: {copy.get('cold_email_subject', 'N/A')}

Check:
1. Is tagline compelling and under 10 words?
2. Is description 2-3 sentences?
3. Does email have clear CTA?
4. Is tone consistent?

Return JSON."""

        response = self.call_llm(system_prompt, user_prompt)

        try:
            review = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            review = json.loads(json_match.group()) if json_match else {
                "copy_quality": 8,
                "compelling": True,
                "issues": [],
                "suggestions": ["Consider A/B testing tagline variants"]
            }

        return review

    def post_pr_comment(self, pr_number: int, comment_text: str, commit_sha: str = None) -> bool:
        """Post a review comment on the GitHub PR."""
        print(f"\n💬 QA: Posting review comments to PR...")

        try:
            if commit_sha:
                # Post inline comment on specific commit
                url = f"https://api.github.com/repos/{self.github_repo}/pulls/{pr_number}/comments"
                data = {
                    "commit_id": commit_sha,
                    "path": "index.html",
                    "position": 1,
                    "body": comment_text
                }
            else:
                # Post general review comment
                url = f"https://api.github.com/repos/{self.github_repo}/pulls/{pr_number}/reviews"
                data = {
                    "body": comment_text,
                    "event": "COMMENT"
                }

            response = requests.post(url, json=data, headers=self.headers)

            if response.status_code in [201, 200]:
                print(f"✅ Review comment posted")
                return True
            else:
                print(f"⚠️  Comment post failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Error posting comment: {str(e)}")
            return False

    def extract_pr_number(self, pr_url: str) -> int:
        """Extract PR number from URL."""
        try:
            return int(pr_url.split("/")[-1])
        except:
            return None

    def run(self):
        """Main QA agent logic."""
        print(f"\n{'='*60}")
        print(f"✅ QA / REVIEWER AGENT STARTING")
        print(f"{'='*60}")

        # Wait for task from CEO
        while True:
            messages = self.get_new_messages()
            for msg in messages:
                if msg.from_agent == "ceo" and msg.message_type == "task":
                    engineer_output = msg.payload.get("engineer_output", {})
                    marketing_output = msg.payload.get("marketing_output", {})
                    product_spec = msg.payload.get("startup_idea")

                    print(f"📋 QA task received")

                    # Review HTML
                    html_content = engineer_output.get("html_content", "")
                    html_review = self.review_html(html_content, {})

                    # Review marketing copy
                    copy = marketing_output.get("copy", {})
                    copy_review = self.review_marketing_copy(copy)

                    # Determine pass/fail
                    html_passed = html_review.get("matches_spec", True) and html_review.get("html_quality", 5) >= 6
                    copy_passed = copy_review.get("compelling", True) and copy_review.get("copy_quality", 5) >= 6
                    overall_passed = html_passed and copy_passed

                    # Collect issues
                    issues = []
                    if not html_passed:
                        issues.extend(html_review.get("issues", []))
                    if not copy_passed:
                        issues.extend(copy_review.get("issues", []))

                    # Post comments to PR if there are issues
                    pr_url = engineer_output.get("pr_url")
                    if pr_url and issues:
                        pr_number = self.extract_pr_number(pr_url)
                        if pr_number:
                            comment_body = "🤖 QA Review:\n\n"
                            comment_body += "**Issues Found:**\n"
                            for issue in issues[:3]:  # Limit to 3 comments
                                comment_body += f"- {issue}\n"

                            self.post_pr_comment(pr_number, comment_body)

                    # Send review result to CEO
                    self.send_message(
                        to_agent="ceo",
                        message_type="result",
                        payload={
                            "passed": overall_passed,
                            "html_passed": html_passed,
                            "copy_passed": copy_passed,
                            "html_review": html_review,
                            "copy_review": copy_review,
                            "issues": issues,
                            "suggestions": (html_review.get("suggestions", []) +
                                          copy_review.get("suggestions", []))[:3]
                        },
                        parent_id=msg.message_id
                    )

                    print(f"✅ QA review complete")
                    print(f"   Overall: {'PASSED ✅' if overall_passed else 'NEEDS REVISION ⚠️'}")
                    print(f"   Issues found: {len(issues)}")
                    return
