"""
Test LLM Agent with calendar function calling
"""

import os
from dotenv import load_dotenv
from agent.llm_agent import LLMAgent
from agent.tools import calendar_tools
from datetime import datetime

load_dotenv()

def test_agent():
    print("=" * 60)
    print("🧪 TESTING LLM AGENT WITH FUNCTION CALLING")
    print("=" * 60)
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found!")
        return
    
    # Initialize calendar tools
    print("\n1️⃣ Initializing calendar tools...")
    calendar_tools.initialize_calendar_agent()
    print("   ✅ Done!")
    
    # Initialize agent with calendar
    print("\n2️⃣ Initializing LLM Agent...")
    agent = LLMAgent(
        api_key=api_key,
        model_name="gemini-2.0-flash-exp",
        enable_calendar=True
    )
    print("   ✅ Done!")
    
    # Test scenarios
    test_cases = [
        {
            "name": "Chat biasa",
            "input": "halo apa kabar?",
            "expect": "Should respond normally without tool"
        },
        {
            "name": "Schedule event",
            "input": f"jadwalin meeting besok jam 3 sore",
            "expect": "Should call add_calendar_event"
        },
        {
            "name": "List events",
            "input": "apa jadwalku hari ini?",
            "expect": "Should call list_calendar_events"
        },
    ]
    
    user_id = "test_user_123"
    
    for idx, test in enumerate(test_cases, 3):
        print(f"\n{idx}️⃣ Test: {test['name']}")
        print(f"   Input: \"{test['input']}\"")
        print(f"   Expect: {test['expect']}")
        print(f"\n   Response:")
        print("   " + "-" * 50)
        
        response = agent.process(user_id, test['input'])
        
        # Print response (indented)
        for line in response.split('\n'):
            print(f"   {line}")
        
        print("   " + "-" * 50)
    
    print("\n" + "=" * 60)
    print("✅ AGENT TESTS COMPLETED")
    print("=" * 60)
    print("\n💡 Check Google Calendar to verify events were created!")

if __name__ == "__main__":
    test_agent()