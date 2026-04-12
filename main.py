#!/usr/bin/env python3
"""
LaunchMind - Multi-Agent System for Autonomous Startup Building

This is the main entry point that orchestrates all agents.
Run this to start the entire system end-to-end.
"""

import os
import sys
import threading
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add agents directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))

from message_bus import message_bus
from agents.ceo_agent import CEOAgent
from agents.product_agent import ProductAgent
from agents.engineer_agent import EngineerAgent
from agents.marketing_agent import MarketingAgent
from agents.qa_agent import QAAgent


def validate_env():
    """Validate required environment variables."""
    required_vars = [
        "OPENAI_API_KEY",
        "GITHUB_TOKEN",
        "GITHUB_REPO",
        "SLACK_BOT_TOKEN",
        "SENDGRID_FROM_EMAIL",
        "SENDGRID_TO_EMAIL"
    ]

    missing = []
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)

    if missing:
        print("❌ Missing environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nCreate a .env file with these variables (use .env.example as template)")
        sys.exit(1)

    print("✅ All environment variables validated")


def run_agent_in_thread(agent, run_args=None):
    """Run an agent in a separate thread."""
    def thread_target():
        try:
            if run_args:
                agent.run(*run_args)
            else:
                agent.run()
        except Exception as e:
            print(f"❌ Error in {agent.name} agent: {str(e)}")
            import traceback
            traceback.print_exc()

    thread = threading.Thread(target=thread_target, daemon=True)
    thread.start()
    return thread


def main():
    """Main orchestration function."""

    print("\n" + "="*80)
    print("🚀 LAUNCHMIND - MULTI-AGENT STARTUP BUILDER")
    print("="*80)

    # Validate environment
    print("\n1️⃣  Validating environment...")
    validate_env()

    # Startup idea
    startup_idea = "AutoTest: An AI-powered CLI tool that automatically generates comprehensive test cases from Python docstrings"

    print(f"\n2️⃣  Startup Idea:")
    print(f"   {startup_idea}")

    # Initialize agents
    print(f"\n3️⃣  Initializing agents...")
    ceo = CEOAgent()
    product = ProductAgent()
    engineer = EngineerAgent()
    marketing = MarketingAgent()
    qa = QAAgent()
    print("   ✅ 5 agents initialized (CEO, Product, Engineer, Marketing, QA)")

    # Start agents in threads
    print(f"\n4️⃣  Starting agent threads...")

    # Start all agents (they wait for messages)
    product_thread = run_agent_in_thread(product)
    engineer_thread = run_agent_in_thread(engineer)
    marketing_thread = run_agent_in_thread(marketing)
    qa_thread = run_agent_in_thread(qa)

    # Give agents time to start
    time.sleep(1)

    # CEO orchestrates everything (this is sequential)
    print(f"\n5️⃣  CEO orchestrating startup launch...")
    ceo.run(startup_idea)

    # Wait for all threads to complete
    print(f"\n6️⃣  Waiting for agents to complete...")
    threads = [product_thread, engineer_thread, marketing_thread, qa_thread]
    timeout = 60  # 60 second timeout
    start_time = time.time()

    for thread in threads:
        remaining = timeout - (time.time() - start_time)
        if remaining > 0:
            thread.join(timeout=remaining)

    # Print final message history
    print(f"\n7️⃣  EXECUTION COMPLETE")
    message_bus.print_history()

    print(f"\n{'='*80}")
    print("✅ LaunchMind startup launch sequence completed!")
    print("="*80)

    # Print summary
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   GitHub PR: Check your repository")
    print(f"   Slack: Check #launches channel")
    print(f"   Email: Check your inbox")
    print(f"   Total Messages: {len(message_bus.all_messages)}")
    print(f"\n   To view full message history, see above output.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
