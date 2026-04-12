"""CEO Agent - Orchestrates all other agents with reasoning and feedback loops."""
import json
from base_agent import BaseAgent
from message_bus import message_bus

class CEOAgent(BaseAgent):
    """CEO orchestrator agent with LLM-based reasoning and decision-making."""

    def __init__(self):
        super().__init__("ceo")
        self.startup_idea = None
        self.product_spec = None
        self.engineer_output = None
        self.marketing_output = None
        self.qa_output = None
        self.revision_cycles = 0

    def decompose_idea(self, startup_idea: str) -> dict:
        """Use LLM to decompose startup idea into tasks for each agent."""
        print(f"\n🧠 CEO: Analyzing startup idea with LLM...")

        system_prompt = """You are a CEO analyzing a startup idea. Break it down into specific, focused tasks
for your team of agents. Return a JSON object with three top-level keys: product_task, engineer_task, marketing_task.
Each should be a clear, actionable task description."""

        user_prompt = f"""Startup Idea: {startup_idea}

Please decompose this into tasks for:
1. Product Agent: Create a product specification
2. Engineer Agent: Build a landing page
3. Marketing Agent: Generate marketing copy and send outreach

Return valid JSON with keys: product_task, engineer_task, marketing_task"""

        response = self.call_llm(system_prompt, user_prompt)
        try:
            tasks = json.loads(response)
            return tasks
        except json.JSONDecodeError:
            # If LLM doesn't return valid JSON, extract it
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                tasks = json.loads(json_match.group())
                return tasks
            raise ValueError("Could not parse LLM response as JSON")

    def send_task_to_agent(self, agent_name: str, task: str) -> None:
        """Send a task to a sub-agent."""
        self.send_message(
            to_agent=agent_name,
            message_type="task",
            payload={
                "startup_idea": self.startup_idea,
                "task": task
            }
        )
        print(f"✉️  CEO: Sent task to {agent_name}")

    def review_agent_output(self, output: dict, agent_name: str) -> tuple[bool, str]:
        """Use LLM to review an agent's output and decide if it's acceptable."""
        print(f"\n🧠 CEO: Reviewing {agent_name}'s output...")

        system_prompt = f"""You are a CEO reviewing {agent_name}'s work on the startup idea: {self.startup_idea}
Review the output and decide:
1. Is it specific and well-detailed?
2. Does it address the task?
3. Is there anything missing or unclear?

Return a JSON object with keys: "acceptable" (boolean), "feedback" (string with specific issues if not acceptable)"""

        user_prompt = f"""Review this {agent_name} output:
{json.dumps(output, indent=2)}

Return JSON with keys: acceptable, feedback"""

        response = self.call_llm(system_prompt, user_prompt)
        try:
            review = json.loads(response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            review = json.loads(json_match.group()) if json_match else {"acceptable": True}

        acceptable = review.get("acceptable", True)
        feedback = review.get("feedback", "")
        return acceptable, feedback

    def request_revision(self, agent_name: str, feedback: str, parent_msg_id: str) -> None:
        """Send a revision request to an agent with specific feedback."""
        self.send_message(
            to_agent=agent_name,
            message_type="revision_request",
            payload={
                "feedback": feedback,
                "startup_idea": self.startup_idea,
                "reason": "CEO review indicated issues. Please revise and resubmit."
            },
            parent_id=parent_msg_id
        )
        self.revision_cycles += 1
        print(f"🔄 CEO: Sent revision request to {agent_name} (Cycle {self.revision_cycles})")

    def run(self, startup_idea: str) -> None:
        """Main CEO orchestration logic."""
        self.startup_idea = startup_idea
        print(f"\n{'='*80}")
        print(f"🚀 CEO AGENT STARTING")
        print(f"Startup Idea: {startup_idea}")
        print(f"{'='*80}")

        # Step 1: Decompose idea into tasks
        print(f"\n1️⃣  DECOMPOSING STARTUP IDEA...")
        tasks = self.decompose_idea(startup_idea)

        # Step 2: Send tasks to agents
        print(f"\n2️⃣  SENDING TASKS TO AGENTS...")
        self.send_task_to_agent("product", tasks.get("product_task", "Create product specification"))
        self.send_task_to_agent("engineer", tasks.get("engineer_task", "Build landing page"))
        self.send_task_to_agent("marketing", tasks.get("marketing_task", "Generate marketing materials"))

        # Step 3: Wait for and review Product output
        print(f"\n3️⃣  WAITING FOR PRODUCT SPEC...")
        while True:
            messages = self.get_new_messages()
            for msg in messages:
                if msg.from_agent == "product" and msg.message_type == "result":
                    self.product_spec = msg.payload
                    print(f"✅ Received Product Spec")

                    # Review the spec
                    acceptable, feedback = self.review_agent_output(msg.payload, "Product")
                    if not acceptable:
                        print(f"⚠️  CEO: Product spec needs revision: {feedback}")
                        self.request_revision("product", feedback, msg.message_id)
                        # In a real system, would loop back. For now, accept with feedback
                    break

        # Step 4: Engineer and Marketing run in parallel (simulate by sending both)
        print(f"\n4️⃣  ENGINEER AND MARKETING WORKING...")
        engineer_msg_id = None
        marketing_msg_id = None

        while True:
            messages = self.get_new_messages()
            for msg in messages:
                if msg.from_agent == "engineer" and msg.message_type == "result":
                    self.engineer_output = msg.payload
                    engineer_msg_id = msg.message_id
                    print(f"✅ Received Engineer Output (PR: {msg.payload.get('pr_url', 'pending')})")

                if msg.from_agent == "marketing" and msg.message_type == "result":
                    self.marketing_output = msg.payload
                    marketing_msg_id = msg.message_id
                    print(f"✅ Received Marketing Output")

                if engineer_msg_id and marketing_msg_id:
                    break

            if engineer_msg_id and marketing_msg_id:
                break

        # Step 5: Send to QA for review (if QA agent exists)
        print(f"\n5️⃣  SENDING TO QA FOR REVIEW...")
        if self.engineer_output and self.marketing_output:
            self.send_message(
                to_agent="qa",
                message_type="task",
                payload={
                    "engineer_output": self.engineer_output,
                    "marketing_output": self.marketing_output,
                    "startup_idea": self.startup_idea
                }
            )

            # Wait for QA review
            print(f"⏳ Waiting for QA review...")
            while True:
                messages = self.get_new_messages()
                for msg in messages:
                    if msg.from_agent == "qa" and msg.message_type == "result":
                        self.qa_output = msg.payload
                        print(f"✅ Received QA Review")

                        # If QA says fail, request revisions
                        if not msg.payload.get("passed", False):
                            print(f"⚠️  QA Issues Found:")
                            for issue in msg.payload.get("issues", []):
                                print(f"   - {issue}")
                        break

        # Step 6: Final summary to Slack
        print(f"\n6️⃣  POSTING FINAL SUMMARY TO SLACK...")
        self.send_message(
            to_agent="marketing",
            message_type="task",
            payload={
                "action": "post_final_summary",
                "product_spec": self.product_spec,
                "engineer_output": self.engineer_output,
                "marketing_output": self.marketing_output,
                "startup_idea": self.startup_idea
            }
        )

        print(f"\n{'='*80}")
        print(f"✅ CEO ORCHESTRATION COMPLETE")
        print(f"{'='*80}")
        print(f"\nSummary:")
        print(f"  - Startup: {startup_idea}")
        print(f"  - Product Spec Generated: {bool(self.product_spec)}")
        print(f"  - Engineer Output: {bool(self.engineer_output)}")
        print(f"  - Marketing Output: {bool(self.marketing_output)}")
        print(f"  - Revision Cycles: {self.revision_cycles}")
