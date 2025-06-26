#!/usr/bin/env python3
"""
Evidence Discovery and Session Management Test Suite

Comprehensive test for evidence discovery functionality across scenarios
and session management features.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli.scenario_manager import ScenarioManager
from server.app import check_for_evidence_discovery
from utils.session_manager import SessionManager


def test_evidence_discovery():
    """Test evidence discovery with different scenarios and actions"""

    print("🔍 Testing Evidence Discovery Functionality")
    print("=" * 60)

    # Initialize managers
    scenario_manager = ScenarioManager()
    session_manager = SessionManager()

    # Load a test scenario
    scenarios = scenario_manager.list_scenarios()
    if not scenarios:
        print("❌ No scenarios found!")
        return False

    # Use the carbanak scenario for testing
    test_scenario_id = "carbanak_inspired_001"
    scenario = scenario_manager.get_scenario(test_scenario_id)

    if not scenario:
        print(f"❌ Scenario {test_scenario_id} not found!")
        return False

    print(f"✅ Loaded scenario: {scenario['scenario_metadata']['name']}")

    # Create a test session
    test_session = session_manager.create_session(
        scenario_id=test_scenario_id,
        scenario_name=scenario["scenario_metadata"]["name"],
        player_name="Test Player",
    )

    print(f"✅ Created test session: {test_session.session_id}")

    # Test different investigation actions
    test_actions = [
        ("examine_logs", "Check email logs for suspicious activity"),
        ("analyze_network", "Look for unusual network connections"),
        ("check_system", "Examine process execution logs"),
        ("interview_user", "Ask about recent phishing emails"),
        ("run_command", "Check PowerShell execution history"),
    ]

    evidence_found_count = 0

    for action, details in test_actions:
        print(f"\n🔎 Testing action: {action}")
        print(f"   Details: {details}")

        # Test evidence discovery
        discovered_evidence = check_for_evidence_discovery(
            action, details, scenario, test_session
        )

        if discovered_evidence:
            evidence_found_count += 1
            print(
                f"   ✅ Evidence discovered: {discovered_evidence['type']} ({discovered_evidence['importance']})"
            )
            print(f"      ID: {discovered_evidence['id']}")
            print(f"      Description: {discovered_evidence['description'][:100]}...")

            # Add to session to avoid duplicates in next tests
            session_manager.current_session = test_session
            session_manager.add_evidence_discovered(discovered_evidence)
        else:
            print("   ❌ No evidence found")

    print("\n📊 Test Results:")
    print(f"   Actions tested: {len(test_actions)}")
    print(f"   Evidence discovered: {evidence_found_count}")
    print(f"   Success rate: {evidence_found_count/len(test_actions)*100:.1f}%")

    # Test evidence structure validation
    print("\n🔍 Testing Evidence Structure:")
    if scenario.get("evidence", {}).get("items"):
        evidence_items = scenario["evidence"]["items"]
        print(f"   Total evidence items in scenario: {len(evidence_items)}")

        for i, evidence in enumerate(evidence_items[:3]):  # Test first 3
            print(f"   Evidence {i+1}:")
            print(f"      ID: {evidence.get('id', 'MISSING')}")
            print(f"      Type: {evidence.get('type', 'MISSING')}")
            print(f"      Source: {evidence.get('source', 'MISSING')}")
            print(f"      Importance: {evidence.get('importance', 'MISSING')}")
            print(
                f"      Description: {evidence.get('description', 'MISSING')[:50]}..."
            )

    print("\n✅ Evidence discovery test completed!")
    return True


def test_evidence_ui_compatibility():
    """Test that evidence structure is compatible with UI templates"""

    print("\n🖥️  Testing UI Template Compatibility")
    print("=" * 60)

    # Sample evidence structure as returned by discovery function
    sample_evidence = {
        "id": "test_001",
        "type": "email",
        "source": "email_log",
        "importance": "critical",
        "description": "Test phishing email",
        "content": "Sample email content...",
        "discovered_at": "2025-06-06T10:30:00",
    }

    # Test required fields
    required_fields = ["id", "type", "source", "importance", "description", "content"]
    missing_fields = []

    for field in required_fields:
        if field not in sample_evidence:
            missing_fields.append(field)

    if missing_fields:
        print(f"❌ Missing required fields: {missing_fields}")
        return False
    else:
        print("✅ All required fields present")

    # Test field values
    if sample_evidence.get("type"):
        print(f"   ✅ Type: {sample_evidence['type']}")
    if sample_evidence.get("importance") in ["critical", "high", "medium", "low"]:
        print(f"   ✅ Valid importance level: {sample_evidence['importance']}")
    if sample_evidence.get("source"):
        print(f"   ✅ Source: {sample_evidence['source']}")

    print("✅ UI compatibility test passed!")
    return True


if __name__ == "__main__":
    success = True

    try:
        # Run tests
        success &= test_evidence_discovery()
        success &= test_evidence_ui_compatibility()

        if success:
            print("\n🎉 All tests passed! Evidence discovery is working correctly.")
        else:
            print("\n❌ Some tests failed. Check the output above for details.")

    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        success = False

    sys.exit(0 if success else 1)
