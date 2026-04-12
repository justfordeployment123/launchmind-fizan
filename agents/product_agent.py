"""Product Agent - Creates structured product specifications using LLM."""
import json
import re
from base_agent import BaseAgent


class ProductAgent(BaseAgent):
    """Generates product specs: value prop, personas, features, user stories."""

    def __init__(self):
        super().__init__("product")

    def run(self, startup_idea: str, revision_feedback: str = None) -> dict:
        """Generate a product specification. Returns the spec dict."""
        print(f"   🎯 Product Agent: generating specification via LLM...")

        extra = ""
        if revision_feedback:
            extra = f"\n\nIMPORTANT — the CEO asked you to revise. Address this feedback:\n{revision_feedback}"

        system_prompt = (
            "You are a product manager. Create a product specification. "
            "Return ONLY valid JSON with these keys:\n"
            "- value_proposition (string, one sentence)\n"
            "- personas (array of {name, role, pain_point})\n"
            "- features (array of {name, description, priority} where 1=highest)\n"
            "- user_stories (array of strings in 'As a X, I want Y so that Z' format)"
        )

        user_prompt = (
            f"Create a detailed product spec for:\n{startup_idea}\n\n"
            "Include 2-3 personas, 5 features ranked by priority, and 3 user stories."
            f"{extra}"
        )

        raw = self.call_llm(system_prompt, user_prompt)
        spec = self._parse(raw)
        return spec

    def _parse(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            m = re.search(r'\{.*\}', text, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group())
                except json.JSONDecodeError:
                    pass
        # fallback
        return {
            "value_proposition": "An AI-powered CLI that generates test cases from Python docstrings.",
            "personas": [
                {"name": "Sarah", "role": "Senior Python Dev", "pain_point": "Writing tests is tedious and repetitive"},
                {"name": "Alex", "role": "Startup Tech Lead", "pain_point": "Need fast test coverage without slowing the team"},
                {"name": "Jordan", "role": "Junior Developer", "pain_point": "Unsure what edge cases to test"},
            ],
            "features": [
                {"name": "Docstring Parser", "description": "Extract function signatures and examples from docstrings", "priority": 1},
                {"name": "Test Generator", "description": "Generate pytest-compatible test functions automatically", "priority": 1},
                {"name": "Edge-Case Suggester", "description": "AI identifies boundary conditions and error cases", "priority": 2},
                {"name": "CI/CD Integration", "description": "GitHub Actions workflow for automated test generation", "priority": 3},
                {"name": "Coverage Dashboard", "description": "Visual report showing generated vs manual test coverage", "priority": 4},
            ],
            "user_stories": [
                "As a developer, I want to run autotest on my module so that tests are generated without manual effort",
                "As a tech lead, I want a coverage report so that I can see which functions lack tests",
                "As a junior engineer, I want suggested edge cases so that I write more robust code",
            ],
        }
