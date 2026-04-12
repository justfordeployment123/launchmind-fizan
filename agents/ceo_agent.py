"""CEO Agent - Orchestrates all other agents with LLM reasoning and feedback loops."""
import json
import re
from base_agent import BaseAgent


class CEOAgent(BaseAgent):
    """CEO orchestrator: decomposes idea, reviews outputs, sends revision requests."""

    def __init__(self):
        super().__init__("ceo")
        self.startup_idea = None
        self.product_spec = None
        self.engineer_output = None
        self.marketing_output = None
        self.qa_output = None
        self.revision_cycles = 0

    # ── LLM call #1: decompose idea into agent tasks ────────────────────
    def decompose_idea(self, startup_idea: str) -> dict:
        """Use LLM to break the startup idea into tasks for each agent."""
        self.startup_idea = startup_idea
        print(f"   🧠 CEO: calling LLM to decompose idea...")

        system_prompt = (
            "You are a startup CEO. Given a startup idea, break it into three "
            "concrete tasks — one for your Product manager, one for your Engineer, "
            "and one for your Marketing lead. Return ONLY valid JSON with keys: "
            "product_task, engineer_task, marketing_task. Each value is a string."
        )
        user_prompt = f"Startup idea: {startup_idea}"

        raw = self.call_llm(system_prompt, user_prompt)
        return self._parse_json(raw, fallback={
            "product_task": "Create a product spec with personas, features, user stories",
            "engineer_task": "Build an HTML landing page showcasing the product",
            "marketing_task": "Write tagline, description, cold-email, and social posts",
        })

    # ── LLM call #2: review an agent's output ───────────────────────────
    def review_agent_output(self, output: dict, agent_name: str) -> tuple:
        """Returns (acceptable: bool, feedback: str)."""
        print(f"   🧠 CEO: calling LLM to review {agent_name} output...")

        system_prompt = (
            f"You are a CEO reviewing the {agent_name} agent's work for the "
            f"startup idea: '{self.startup_idea}'. "
            "Evaluate quality: is it specific, complete, and actionable? "
            "Return ONLY valid JSON: {\"acceptable\": true/false, \"feedback\": \"...\"}"
        )
        user_prompt = json.dumps(output, indent=2)[:3000]

        raw = self.call_llm(system_prompt, user_prompt)
        review = self._parse_json(raw, fallback={"acceptable": True, "feedback": "Looks good overall."})
        return review.get("acceptable", True), review.get("feedback", "")

    # ── Send structured task to another agent ────────────────────────────
    def send_task_to_agent(self, agent_name: str, task: str):
        self.send_message(agent_name, "task", {
            "startup_idea": self.startup_idea,
            "task": task,
        })
        print(f"   ✉️  CEO → {agent_name}: task sent")

    # ── Revision request ─────────────────────────────────────────────────
    def request_revision(self, agent_name: str, feedback: str, parent_msg_id: str):
        self.send_message(agent_name, "revision_request", {
            "feedback": feedback,
            "startup_idea": self.startup_idea,
        }, parent_id=parent_msg_id)
        self.revision_cycles += 1
        print(f"   🔄 CEO → {agent_name}: revision request #{self.revision_cycles}")

    # ── helpers ──────────────────────────────────────────────────────────
    @staticmethod
    def _parse_json(text: str, fallback: dict) -> dict:
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

    def run(self, startup_idea=None):
        """Not used directly — main.py drives the orchestration."""
        pass
