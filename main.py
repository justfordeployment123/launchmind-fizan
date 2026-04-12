#!/usr/bin/env python3
"""
LaunchMind - Multi-Agent System for Autonomous Startup Building

Entry point: runs all 5 agents sequentially, orchestrated by the CEO.
Agents communicate via structured JSON messages on a shared message bus.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add agents directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))

from message_bus import message_bus
from ceo_agent import CEOAgent
from product_agent import ProductAgent
from engineer_agent import EngineerAgent
from marketing_agent import MarketingAgent
from qa_agent import QAAgent


def validate_env():
    """Validate required environment variables."""
    required = {
        "OPENAI_API_KEY": "OpenAI API key",
        "GITHUB_TOKEN": "GitHub Personal Access Token",
        "GITHUB_REPO": "GitHub repo (owner/name)",
        "SLACK_BOT_TOKEN": "Slack Bot OAuth Token",
    }
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        print("❌ Missing environment variables:")
        for var in missing:
            print(f"   - {var} ({required[var]})")
        print("\nCreate a .env file — see .env.example")
        sys.exit(1)
    print("✅ All environment variables present")


def main():
    startup_idea = (
        "AutoTest: An AI-powered CLI tool that automatically generates "
        "comprehensive test cases from Python docstrings"
    )

    print("\n" + "=" * 80)
    print("🚀  LAUNCHMIND — MULTI-AGENT STARTUP BUILDER")
    print("=" * 80)

    # ── 1. Validate ──────────────────────────────────────────────────────
    print("\n1️⃣  Validating environment...")
    validate_env()

    print(f"\n2️⃣  Startup Idea:\n   {startup_idea}")

    # ── 2. Init agents ───────────────────────────────────────────────────
    print("\n3️⃣  Initializing agents...")
    ceo       = CEOAgent()
    product   = ProductAgent()
    engineer  = EngineerAgent()
    marketing = MarketingAgent()
    qa        = QAAgent()
    print("   ✅ CEO, Product, Engineer, Marketing, QA — all ready")

    # ── 3. CEO decomposes the idea (LLM reasoning #1) ───────────────────
    print("\n4️⃣  CEO: decomposing startup idea (LLM call #1)...")
    tasks = ceo.decompose_idea(startup_idea)
    print(f"   Tasks generated: {list(tasks.keys())}")

    # Send task messages (recorded on the bus)
    ceo.send_task_to_agent("product",   tasks.get("product_task",   "Create product specification"))
    ceo.send_task_to_agent("engineer",  tasks.get("engineer_task",  "Build landing page"))
    ceo.send_task_to_agent("marketing", tasks.get("marketing_task", "Generate marketing materials"))

    # ── 4. Product Agent generates spec ──────────────────────────────────
    print("\n5️⃣  Product Agent: generating product specification...")
    product_spec = product.run(startup_idea)
    print(f"   ✅ Value prop: {product_spec.get('value_proposition', '?')[:80]}")

    # Record result on bus
    product.send_message("ceo", "result", product_spec)

    # ── 5. CEO reviews product spec (LLM reasoning #2 — feedback loop) ──
    print("\n6️⃣  CEO: reviewing product spec (LLM call #2)...")
    acceptable, feedback = ceo.review_agent_output(product_spec, "Product")

    if not acceptable:
        print(f"   ⚠️  Not acceptable — feedback: {feedback}")
        ceo.request_revision("product", feedback, message_bus.all_messages[-1].message_id)

        # Product revises
        print("   🔄 Product Agent: revising...")
        product_spec = product.run(startup_idea, revision_feedback=feedback)
        product.send_message("ceo", "result", product_spec)
        print(f"   ✅ Revised spec received")
    else:
        print(f"   ✅ Spec accepted (feedback: {feedback[:60]})")

    ceo.product_spec = product_spec

    # Send spec to Engineer & Marketing (via bus)
    product.send_message("engineer",  "task", product_spec)
    product.send_message("marketing", "task", product_spec)

    # ── 6. Engineer Agent — code + GitHub ────────────────────────────────
    print("\n7️⃣  Engineer Agent: generating landing page & pushing to GitHub...")
    engineer_result = engineer.run(product_spec)
    engineer.send_message("ceo", "result", engineer_result)
    ceo.engineer_output = engineer_result

    pr_url    = engineer_result.get("pr_url", "N/A")
    issue_url = engineer_result.get("issue_url", "N/A")
    print(f"   ✅ Issue : {issue_url}")
    print(f"   ✅ PR    : {pr_url}")

    # ── 7. Marketing Agent — copy + email + Slack ────────────────────────
    print("\n8️⃣  Marketing Agent: generating copy, sending email, posting Slack...")
    marketing_result = marketing.run(product_spec, pr_url)
    marketing.send_message("ceo", "result", marketing_result)
    ceo.marketing_output = marketing_result

    print(f"   ✅ Tagline     : {marketing_result.get('tagline', '?')}")
    print(f"   ✅ Email sent  : {marketing_result.get('email_sent', False)}")
    print(f"   ✅ Slack posted: {marketing_result.get('slack_posted', False)}")

    # ── 8. QA Agent — review ─────────────────────────────────────────────
    print("\n9️⃣  QA Agent: reviewing engineer & marketing output...")
    ceo.send_message("qa", "task", {
        "engineer_output": engineer_result,
        "marketing_output": marketing_result,
        "product_spec": product_spec,
        "startup_idea": startup_idea,
    })
    qa_result = qa.run(engineer_result, marketing_result, product_spec, pr_url)
    qa.send_message("ceo", "result", qa_result)
    ceo.qa_output = qa_result

    passed = qa_result.get("passed", True)
    print(f"   ✅ QA verdict: {'PASSED ✅' if passed else 'NEEDS REVISION ⚠️'}")
    for issue in qa_result.get("issues", []):
        print(f"      - {issue}")

    # ── 9. CEO posts final Slack summary ─────────────────────────────────
    print("\n🔟  CEO: posting final summary to Slack...")
    ceo.send_message("marketing", "task", {
        "action": "post_final_summary",
        "startup_idea": startup_idea,
        "product_spec": product_spec,
        "engineer_output": engineer_result,
        "marketing_output": marketing_result,
    })
    marketing.post_to_slack(
        tagline=marketing_result.get("tagline", startup_idea),
        description=marketing_result.get("description", "Check out our startup!"),
        pr_url=pr_url,
    )

    # ── 10. Print full message history ───────────────────────────────────
    message_bus.print_history()

    # ── Done ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("📊  FINAL SUMMARY")
    print("=" * 80)
    print(f"  Startup Idea   : {startup_idea}")
    print(f"  Product Spec   : ✅ generated ({len(product_spec.get('features',[]))} features)")
    print(f"  GitHub Issue   : {issue_url}")
    print(f"  GitHub PR      : {pr_url}")
    print(f"  Email          : {'✅ sent (mock)' if marketing_result.get('email_sent') else '❌'}")
    print(f"  Slack          : {'✅ posted' if marketing_result.get('slack_posted') else '❌'}")
    print(f"  QA             : {'✅ passed' if passed else '⚠️ issues found'}")
    print(f"  Revision Cycles: {ceo.revision_cycles}")
    print(f"  Total Messages : {len(message_bus.all_messages)}")
    print("=" * 80)
    print("✅  LaunchMind execution complete!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
