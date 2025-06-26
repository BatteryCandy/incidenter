#!/usr/bin/env python3
"""
Google AI Credentials Validation Test

This script validates Google AI authentication setup for the Incidenter AI facilitator.
It now supports both API key and Application Default Credentials (ADC).

Usage:
    python tests/test_gcp_credentials.py

Environment Variables:
    GOOGLE_AI_API_KEY - Google AI API key (recommended for development)
    GOOGLE_APPLICATION_CREDENTIALS - Path to service account JSON (for ADC)
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from facilitator.ai_facilitator import get_facilitator


def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print("=" * 60)


def test_credentials():
    """Test Google AI credentials validation"""
    print_header("GOOGLE AI CREDENTIALS TEST")

    print("📋 Environment Check:")
    api_key = os.getenv("GOOGLE_AI_API_KEY")
    adc_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if api_key:
        print(f"✅ GOOGLE_AI_API_KEY: Set (length: {len(api_key)})")
    else:
        print("❌ GOOGLE_AI_API_KEY: Not set")

    if adc_file:
        print(f"✅ GOOGLE_APPLICATION_CREDENTIALS: {adc_file}")
        if os.path.exists(adc_file):
            print("   ✅ File exists")
        else:
            print("   ❌ File does not exist")
    else:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS: Not set")

    # Check for gcloud ADC
    try:
        from google.auth import default as google_default_credentials

        credentials, project = google_default_credentials()
        print(f"✅ gcloud ADC: Available (project: {project})")
    except Exception:
        print("❌ gcloud ADC: Not available")

    print("\n🧪 Testing facilitator initialization...")

    try:
        facilitator = get_facilitator(provider="google")

        if facilitator.provider == "mock":
            print("❌ Authentication failed - using mock facilitator")
            print("\n💡 Setup Instructions:")
            print("1. API Key (Recommended):")
            print("   export GOOGLE_AI_API_KEY='your-api-key-here'")
            print("   Get key at: https://makersuite.google.com/app/apikey")
            print("\n2. ADC (Advanced):")
            print("   gcloud auth login --update-adc")
            return False
        else:
            print(f"✅ Authentication successful using {facilitator.provider} provider")
            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_basic_functionality():
    """Test basic AI functionality"""
    print_header("BASIC FUNCTIONALITY TEST")

    try:
        facilitator = get_facilitator()

        if facilitator.provider == "mock":
            print("⚠️  Using mock facilitator - skipping AI functionality test")
            return False

        print("🎮 Loading test scenario...")
        facilitator.load_scenario(
            {
                "id": "test-scenario",
                "name": "Credential Test Scenario",
                "difficulty": "easy",
                "attack_type": "phishing",
                "timeline": {"start": "2024-01-01T00:00:00Z"},
            }
        )

        print("🔍 Testing investigation action...")
        response = facilitator.facilitate_action(
            action="Analyze network logs",
            details="Looking for suspicious outbound connections",
        )

        if response and response.content:
            print("✅ Investigation action successful")
            print(f"📝 Response: {response.content[:150]}...")
            return True
        else:
            print("❌ Investigation action failed")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_advanced_features():
    """Test advanced AI features"""
    print_header("ADVANCED FEATURES TEST")

    try:
        facilitator = get_facilitator()

        if facilitator.provider == "mock":
            print("⚠️  Using mock facilitator - testing mock responses")

        print("🤔 Testing theory evaluation...")
        theory_response = facilitator.evaluate_theory(
            "The attacker gained initial access through a phishing email and used stolen credentials"
        )

        if theory_response and theory_response.content:
            print("✅ Theory evaluation successful")
            print(f"📝 Feedback: {theory_response.content[:150]}...")

        print("💡 Testing hint system...")
        hint_response = facilitator.provide_hint(
            "Need help understanding the attack timeline"
        )

        if hint_response and hint_response.content:
            print("✅ Hint system successful")
            print(f"💡 Hint: {hint_response.content[:150]}...")
            return True
        else:
            print("❌ Advanced features test failed")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Google AI Credentials Validation")
    print("Testing enhanced authentication with API Key and ADC support")

    # Test 1: Credentials validation
    creds_success = test_credentials()

    # Test 2: Basic functionality
    basic_success = test_basic_functionality()

    # Test 3: Advanced features
    advanced_success = test_advanced_features()

    # Summary
    print_header("TEST SUMMARY")
    print(f"Credentials Validation: {'✅ PASS' if creds_success else '❌ FAIL'}")
    print(f"Basic Functionality: {'✅ PASS' if basic_success else '❌ FAIL'}")
    print(f"Advanced Features: {'✅ PASS' if advanced_success else '❌ FAIL'}")

    if creds_success and basic_success:
        print("\n🎉 SUCCESS: Google AI integration is working correctly!")
        print(
            "🤖 The AI facilitator is ready to enhance your incident response training"
        )
    elif creds_success:
        print(
            "\n⚠️  PARTIAL SUCCESS: Authentication works but functionality issues detected"
        )
    else:
        print("\n❌ SETUP REQUIRED: Authentication not configured")
        print("\n📚 Quick Setup Guide:")
        print("🔑 Option 1 - API Key (Recommended):")
        print("   1. Visit: https://makersuite.google.com/app/apikey")
        print("   2. Create/copy your API key")
        print("   3. Run: export GOOGLE_AI_API_KEY='your-key-here'")
        print("   4. Rerun this test")
        print("\n🌐 Option 2 - ADC (Advanced):")
        print("   1. Install gcloud CLI")
        print("   2. Run: gcloud auth login --update-adc")
        print("   3. Rerun this test")

        sys.exit(1)


if __name__ == "__main__":
    main()
