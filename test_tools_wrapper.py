"""
Test calendar tools wrapper
"""

from agent.tools import calendar_tools
from datetime import datetime, timedelta

def test_wrapper():
    print("=" * 60)
    print("🧪 TESTING CALENDAR TOOLS WRAPPER")
    print("=" * 60)
    
    # Initialize (sekarang path default udah bener)
    print("\n1️⃣ Initializing calendar agent...")
    success = calendar_tools.initialize_calendar_agent()
    
    if not success:
        print("   ❌ Failed to initialize. Check credentials.")
        return
    print("   ✅ Initialized!")
    
    # Test add
    print("\n2️⃣ Testing add_calendar_event...")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    result = calendar_tools.add_calendar_event(
        title="🧪 Test from Wrapper",
        date=tomorrow,
        time="14:00",
        duration=60
    )
    print(result['message'])
    
    if result['success']:
        event_id = result['event_id']
    else:
        return
    
    # Test list
    print("\n3️⃣ Testing list_calendar_events...")
    result = calendar_tools.list_calendar_events(days=7)
    print(result['message'][:500] + "..." if len(result['message']) > 500 else result['message'])
    
    # Test update
    print("\n4️⃣ Testing update_calendar_event...")
    result = calendar_tools.update_calendar_event(
        event_id=event_id,
        title="🧪 UPDATED Test"
    )
    print(result['message'])
    
    # Test delete
    print("\n5️⃣ Testing delete_calendar_event...")
    result = calendar_tools.delete_calendar_event(event_id)
    print(result['message'])
    
    print("\n" + "=" * 60)
    print("✅ ALL WRAPPER TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_wrapper()