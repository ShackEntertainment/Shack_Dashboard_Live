"""
Shack Entertainment - Test Suite
Run this to test all components
"""

from chief_of_staff import ChiefOfStaff
from agent_router import AgentRouter
from config import ensure_directories, AGENT_IDS

def run_tests():
    """Run all tests"""
    print("="*60)
    print("SHACK ENTERTAINMENT - TEST SUITE")
    print("="*60)
    
    # Ensure directories exist
    ensure_directories()
    print("✓ Directories initialized")
    
    # Test Chief of Staff
    print("\n--- Testing Chief of Staff ---")
    cos = ChiefOfStaff()
    cos.display_status()
    
    # Test adding talent
    test_artist = {
        "name": "Test Artist",
        "category": "Painters",
        "status": "Active",
        "email": "test@example.com",
        "portfolio": "https://example.com",
        "bio": "Test bio",
        "managed_by_shack": "Yes",
        "notes": "Test notes",
        "source": "Test Suite"
    }
    
    result = cos.add_talent("Artists_Unlimited", test_artist)
    assert result == True, "Failed to add talent"
    print("✓ Talent addition test passed")
    
    # Test routing
    agent_id = cos.route_work("artist_bio", {"artist": "Test"})
    assert agent_id == AGENT_IDS["CREATIVE_DIRECTOR"], "Routing failed"
    print("✓ Work routing test passed")
    
    # Test Agent Router
    print("\n--- Testing Agent Router ---")
    router = AgentRouter()
    router.route_message(
        AGENT_IDS["CHIEF_OF_STAFF"],
        AGENT_IDS["CREATIVE_DIRECTOR"],
        {"test": "message"}
    )
    
    messages = router.get_pending_messages(AGENT_IDS["CREATIVE_DIRECTOR"])
    assert len(messages) == 1, "Message routing failed"
    print("✓ Agent routing test passed")
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED ✓")
    print("="*60)

if __name__ == "__main__":
    run_tests()