#!/usr/bin/env python3
"""
Test script for Incidenter web interface
Tests the complete gameplay flow through API endpoints
"""

import requests

# Base URL for the Flask server
BASE_URL = "http://127.0.0.1:5003"


def test_scenario_list():
    """Test scenario listing"""
    print("🧪 Testing scenario list...")
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        print("✅ Home page loads successfully")
        return True
    else:
        print(f"❌ Home page failed: {response.status_code}")
        return False


def test_scenario_detail():
    """Test scenario detail page"""
    print("🧪 Testing scenario detail...")
    response = requests.get(f"{BASE_URL}/scenario/wannacry_inspired")
    if response.status_code == 200:
        print("✅ Scenario detail page loads successfully")
        return True
    else:
        print(f"❌ Scenario detail failed: {response.status_code}")
        return False


def test_start_game():
    """Test starting a game session"""
    print("🧪 Testing game start...")

    # Create a session to maintain cookies
    session = requests.Session()

    # Start a game
    data = {"player_name": "Test Player"}
    response = session.post(
        f"{BASE_URL}/start/wannacry_inspired", data=data, allow_redirects=False
    )

    if response.status_code == 302:  # Redirect to play page
        print("✅ Game started successfully")

        # Test the play page
        play_response = session.get(f"{BASE_URL}/play")
        if play_response.status_code == 200:
            print("✅ Game interface loads successfully")
            return session
        else:
            print(f"❌ Game interface failed: {play_response.status_code}")
            return None
    else:
        print(f"❌ Game start failed: {response.status_code}")
        return None


def test_session_status(session):
    """Test session status API"""
    print("🧪 Testing session status...")
    response = session.get(f"{BASE_URL}/api/session_status")
    if response.status_code == 200:
        data = response.json()
        if data.get("active"):
            print(
                f"✅ Session active: {data.get('scenario_name')} - {data.get('player_name')}"
            )
            return True
        else:
            print("❌ Session not active")
            return False
    else:
        print(f"❌ Session status failed: {response.status_code}")
        return False


def test_investigation_action(session):
    """Test investigation action"""
    print("🧪 Testing investigation action...")
    data = {"action": "Check system logs for suspicious activity"}
    response = session.post(f"{BASE_URL}/api/investigate", json=data)

    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"✅ Investigation successful: {result.get('message', 'No message')}")
            return True
        else:
            print(f"❌ Investigation failed: {result.get('error')}")
            return False
    else:
        print(f"❌ Investigation request failed: {response.status_code}")
        return False


def test_get_hint(session):
    """Test getting a hint"""
    print("🧪 Testing hint system...")
    response = session.get(f"{BASE_URL}/api/get_hint")

    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"✅ Hint received: {result.get('hint')}")
            return True
        else:
            print(f"❌ Hint failed: {result.get('error')}")
            return False
    else:
        print(f"❌ Hint request failed: {response.status_code}")
        return False


def test_submit_theory(session):
    """Test submitting a theory"""
    print("🧪 Testing theory submission...")
    data = {
        "theory": "The attack appears to be a ransomware incident using the WannaCry variant, "
        "exploiting the SMB vulnerability to spread laterally across the network."
    }
    response = session.post(f"{BASE_URL}/api/submit_theory", json=data)

    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"✅ Theory submitted: {result.get('feedback')}")
            print(f"   Accuracy score: {result.get('accuracy_score', 'N/A')}")
            return True
        else:
            print(f"❌ Theory submission failed: {result.get('error')}")
            return False
    else:
        print(f"❌ Theory request failed: {response.status_code}")
        return False


def run_tests():
    """Run all tests"""
    print("🚀 Starting Incidenter Web Interface Tests\n")

    tests_passed = 0
    total_tests = 6

    # Test basic pages
    if test_scenario_list():
        tests_passed += 1

    if test_scenario_detail():
        tests_passed += 1

    # Test game flow
    session = test_start_game()
    if session:
        tests_passed += 1

        if test_session_status(session):
            tests_passed += 1

        if test_investigation_action(session):
            tests_passed += 1

        if test_get_hint(session):
            tests_passed += 1

        # Optional: Test theory submission
        test_submit_theory(session)

    print(f"\n🏁 Tests completed: {tests_passed}/{total_tests} passed")

    if tests_passed == total_tests:
        print("🎉 All core tests passed! The web interface is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    try:
        run_tests()
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted")
    except Exception as e:
        print(f"\n💥 Test error: {e}")
