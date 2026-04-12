"""Product Agent - Creates product specifications."""
import json
from base_agent import BaseAgent

class ProductAgent(BaseAgent):
    """Product agent that generates comprehensive product specifications."""

    def __init__(self):
        super().__init__("product")

    def generate_spec(self, startup_idea: str) -> dict:
        """Use LLM to generate a complete product specification."""
        print(f"\n🎯 Product: Generating specification...")

        system_prompt = """You are a product manager. Create a comprehensive product specification in valid JSON.
Return a JSON object with these exact keys:
- value_proposition: string (one sentence)
- personas: array of objects with name, role, pain_point
- features: array of objects with name, description, priority (1-5, 1 is highest)
- user_stories: array of strings in 'As a X, I want Y so that Z' format"""

        user_prompt = f"""Create a detailed product specification for this startup:
{startup_idea}

Requirements:
1. value_proposition: One compelling sentence about what this product does
2. personas: At least 2-3 detailed user personas with names and specific pain points
3. features: 5 core features ranked by priority
4. user_stories: 3 user stories in standard format

Return ONLY valid JSON, no other text."""

        response = self.call_llm(system_prompt, user_prompt)

        try:
            spec = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            spec = json.loads(json_match.group()) if json_match else self._default_spec()

        return spec

    def _default_spec(self) -> dict:
        """Fallback specification."""
        return {
            "value_proposition": "An AI-powered tool that generates test cases from Python docstrings",
            "personas": [
                {
                    "name": "Junior Dev",
                    "role": "Python developer",
                    "pain_point": "Writing comprehensive tests is time-consuming"
                },
                {
                    "name": "Startup Tech Lead",
                    "role": "Team lead at startup",
                    "pain_point": "Need fast testing without sacrificing quality"
                }
            ],
            "features": [
                {"name": "Docstring Parsing", "description": "Automatically extract test cases from docstrings", "priority": 1},
                {"name": "Test Generation", "description": "Generate pytest-compatible test code", "priority": 1},
                {"name": "Edge Case Detection", "description": "AI identifies edge cases to test", "priority": 2},
                {"name": "CI/CD Integration", "description": "Integrate with GitHub Actions", "priority": 3},
                {"name": "Test Coverage Reports", "description": "Generate coverage reports", "priority": 4}
            ],
            "user_stories": [
                "As a developer, I want to paste Python code so that AutoTest generates tests automatically",
                "As a tech lead, I want test coverage metrics so that I can ensure code quality",
                "As a junior engineer, I want suggested edge cases so that I write more robust tests"
            ]
        }

    def run(self):
        """Main product agent logic."""
        print(f"\n{'='*60}")
        print(f"👤 PRODUCT AGENT STARTING")
        print(f"{'='*60}")

        # Wait for task from CEO
        while True:
            messages = self.get_new_messages()
            for msg in messages:
                if msg.from_agent == "ceo" and msg.message_type == "task":
                    startup_idea = msg.payload.get("startup_idea")
                    print(f"📋 Task received: {msg.payload.get('task')}")

                    # Generate product spec
                    spec = self.generate_spec(startup_idea)

                    # Send result back to CEO
                    self.send_message(
                        to_agent="ceo",
                        message_type="result",
                        payload=spec,
                        parent_id=msg.message_id
                    )

                    # Also send to Engineer and Marketing
                    self.send_message(to_agent="engineer", message_type="task", payload=spec)
                    self.send_message(to_agent="marketing", message_type="task", payload=spec)

                    print(f"✅ Product spec generated and sent")
                    print(f"   Value Prop: {spec.get('value_proposition', 'N/A')[:80]}...")
                    print(f"   Features: {len(spec.get('features', []))} identified")
                    print(f"   Personas: {len(spec.get('personas', []))} personas")

                    return  # Product agent completes after first spec
