"""QA / Reviewer Agent - Reviews Engineer and Marketing outputs using LLM."""
import json
import os
import re
import requests
from base_agent import BaseAgent


class QAAgent(BaseAgent):
    """Reviews HTML and marketing copy, posts PR comments, returns verdict."""

    def __init__(self):
        super().__init__("qa")
        self.token = os.environ.get("GITHUB_TOKEN", "")
        self.repo = os.environ.get("GITHUB_REPO", "")
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github+json",
        }

    # ── public entry point ───────────────────────────────────────────────
    def run(self, engineer_output: dict, marketing_output: dict,
            product_spec: dict, pr_url: str) -> dict:
        """Review outputs and post PR comments. Returns review dict."""

        html_review = self._review_html(engineer_output, product_spec)
        copy_review = self._review_copy(marketing_output, product_spec)

        # Determine pass/fail
        html_ok = html_review.get("score", 7) >= 6
        copy_ok = copy_review.get("score", 7) >= 6
        passed = html_ok and copy_ok

        all_issues = html_review.get("issues", []) + copy_review.get("issues", [])
        all_suggestions = html_review.get("suggestions", []) + copy_review.get("suggestions", [])

        # Post PR review comments
        self._post_pr_review(pr_url, html_review, copy_review)

        return {
            "passed": passed,
            "html_passed": html_ok,
            "copy_passed": copy_ok,
            "html_review": html_review,
            "copy_review": copy_review,
            "issues": all_issues[:5],
            "suggestions": all_suggestions[:5],
        }

    # ── LLM: review HTML ────────────────────────────────────────────────
    def _review_html(self, eng: dict, spec: dict) -> dict:
        print(f"   🔍 QA: reviewing HTML via LLM...")

        system_prompt = (
            "You are a QA reviewer. Review this HTML landing page. "
            "Return JSON with: score (1-10), issues (array of strings), "
            "suggestions (array of strings)."
        )
        user_prompt = (
            f"Product: {spec.get('value_proposition', '?')}\n\n"
            f"HTML excerpt:\n{eng.get('html_content', 'N/A')[:1500]}\n\n"
            "Check: does the headline match the product? Are features listed? "
            "Is there a CTA button? Is CSS present?"
        )

        raw = self.call_llm(system_prompt, user_prompt)
        return self._parse(raw, {"score": 8, "issues": [], "suggestions": []})

    # ── LLM: review copy ────────────────────────────────────────────────
    def _review_copy(self, mkt: dict, spec: dict) -> dict:
        print(f"   🔍 QA: reviewing marketing copy via LLM...")

        copy = mkt.get("copy", {})
        system_prompt = (
            "You are a marketing QA reviewer. Review this copy. "
            "Return JSON with: score (1-10), issues (array of strings), "
            "suggestions (array of strings)."
        )
        user_prompt = (
            f"Tagline: {copy.get('tagline', 'N/A')}\n"
            f"Description: {copy.get('description', 'N/A')}\n"
            f"Email subject: {copy.get('cold_email_subject', 'N/A')}\n\n"
            "Check: tagline under 10 words? Description 2-3 sentences? "
            "Email has clear CTA? Tone consistent?"
        )

        raw = self.call_llm(system_prompt, user_prompt)
        return self._parse(raw, {"score": 8, "issues": [], "suggestions": []})

    # ── Post review comment on PR ────────────────────────────────────────
    def _post_pr_review(self, pr_url: str, html_review: dict, copy_review: dict):
        pr_number = self._extract_pr_number(pr_url)
        if not pr_number:
            print(f"   ⚠️  Cannot post PR comment — no PR number")
            return

        body_parts = ["## 🤖 QA Agent Review\n"]

        body_parts.append("### HTML Landing Page")
        body_parts.append(f"**Score:** {html_review.get('score', '?')}/10\n")
        for issue in html_review.get("issues", [])[:3]:
            body_parts.append(f"- ⚠️ {issue}")
        for s in html_review.get("suggestions", [])[:2]:
            body_parts.append(f"- 💡 {s}")

        body_parts.append("\n### Marketing Copy")
        body_parts.append(f"**Score:** {copy_review.get('score', '?')}/10\n")
        for issue in copy_review.get("issues", [])[:3]:
            body_parts.append(f"- ⚠️ {issue}")
        for s in copy_review.get("suggestions", [])[:2]:
            body_parts.append(f"- 💡 {s}")

        comment_body = "\n".join(body_parts)

        try:
            r = requests.post(
                f"https://api.github.com/repos/{self.repo}/issues/{pr_number}/comments",
                headers=self.headers,
                json={"body": comment_body},
            )
            if r.status_code == 201:
                print(f"   ✅ QA review comment posted on PR #{pr_number}")
            else:
                print(f"   ⚠️  PR comment returned {r.status_code}: {r.text[:100]}")
        except Exception as e:
            print(f"   ❌ PR comment error: {e}")

    # ── helpers ──────────────────────────────────────────────────────────
    @staticmethod
    def _extract_pr_number(url: str):
        try:
            return int(url.rstrip("/").split("/")[-1])
        except (ValueError, IndexError):
            return None

    @staticmethod
    def _parse(text: str, fallback: dict) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group())
                except json.JSONDecodeError:
                    pass
        return fallback
