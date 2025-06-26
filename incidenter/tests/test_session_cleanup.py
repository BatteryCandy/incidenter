#!/usr/bin/env python3
"""
Test script to verify session cleanup functionality
"""

import tempfile
import json
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path so we can import from utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.session_manager import SessionManager


def create_test_session_file(sessions_dir: Path, session_id: str, start_time: datetime):
    """Create a test session file with a specific timestamp"""
    session_data = {
        "session_id": session_id,
        "scenario_id": "test_scenario",
        "scenario_name": "Test Scenario",
        "player_name": "Test Player",
        "start_time": start_time.isoformat(),
        "current_phase": "Initial Access",
        "investigation_actions": [],
        "evidence_discovered": [],
        "theories_submitted": [],
        "hints_used": 0,
        "score_checkpoints": [],
        "is_completed": False,
        "completion_time": None,
        "final_score": None,
        "session_notes": "",
        "metadata": {"created_at": start_time.isoformat(), "version": "1.0"},
    }

    session_file = sessions_dir / f"{session_id}.json"
    with open(session_file, "w") as f:
        json.dump(session_data, f, indent=2)

    # Set the file modification time to match the start_time
    timestamp = start_time.timestamp()
    os.utime(session_file, (timestamp, timestamp))


def test_session_cleanup():
    """Test that session cleanup keeps only the last 10 sessions"""
    print("🧪 Testing Session Cleanup Functionality")
    print("=" * 50)

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        sessions_dir = Path(temp_dir) / "test_sessions"
        sessions_dir.mkdir()

        print(f"📁 Using temp directory: {sessions_dir}")

        # Create 15 test sessions with different timestamps
        base_time = datetime.now()
        session_ids = []

        for i in range(15):
            session_id = f"test_session_{i:02d}"
            session_time = base_time - timedelta(
                hours=i
            )  # Older sessions have earlier times
            create_test_session_file(sessions_dir, session_id, session_time)
            session_ids.append(session_id)

        print("✅ Created 15 test sessions")

        # Verify all 15 sessions exist
        existing_files = list(sessions_dir.glob("*.json"))
        assert (
            len(existing_files) == 15
        ), f"Expected 15 files, found {len(existing_files)}"

        print("✅ Verified all 15 session files exist")

        # Initialize SessionManager with max_sessions=10
        session_manager = SessionManager(
            sessions_dir=str(sessions_dir), max_sessions=10
        )

        # Trigger cleanup manually
        cleaned_up = session_manager.cleanup_sessions()

        print(f"🧹 Cleanup removed {cleaned_up} sessions")

        # Verify only 10 sessions remain
        remaining_files = list(sessions_dir.glob("*.json"))
        remaining_count = len(remaining_files)

        print(f"📊 Sessions remaining: {remaining_count}")

        if remaining_count == 10:
            print("✅ Cleanup successful: exactly 10 sessions remain")
        else:
            print(f"❌ Cleanup failed: expected 10 sessions, found {remaining_count}")
            return False

        # Verify that the most recent sessions were kept
        remaining_ids = [f.stem for f in remaining_files]
        expected_ids = [
            f"test_session_{i:02d}" for i in range(10)
        ]  # Most recent are 0-9

        remaining_ids.sort()
        expected_ids.sort()

        if remaining_ids == expected_ids:
            print("✅ Correct sessions were kept (most recent 10)")
        else:
            print(
                f"❌ Wrong sessions kept. Expected: {expected_ids}, Got: {remaining_ids}"
            )
            return False

        # Test automatic cleanup on save
        print("\n🔄 Testing automatic cleanup on save...")

        # Create a new session (this should trigger cleanup)
        new_session = session_manager.create_session(  # noqa: F841
            scenario_id="auto_test_scenario",
            scenario_name="Auto Test Scenario",
            player_name="Auto Test Player",
        )  # noqa: F841

        # Should still have 10 sessions (oldest was removed, new one added)
        final_files = list(sessions_dir.glob("*.json"))
        final_count = len(final_files)

        print(f"📊 Sessions after creating new session: {final_count}")

        if final_count == 10:
            print("✅ Automatic cleanup on save working correctly")
            return True
        else:
            print(
                f"❌ Automatic cleanup failed: expected 10 sessions, found {final_count}"
            )
            return False


def main():
    """Run the test"""
    try:
        success = test_session_cleanup()

        print("\n" + "=" * 50)
        if success:
            print("🎉 All session cleanup tests passed!")
            print("\n📝 Summary of improvements:")
            print("- Sessions are automatically limited to 10 most recent")
            print("- Cleanup happens automatically when saving sessions")
            print(
                "- Manual cleanup method available: session_manager.cleanup_sessions()"
            )
            print("- Configurable max sessions via SessionManager(max_sessions=N)")
            return 0
        else:
            print("❌ Session cleanup tests failed!")
            return 1

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
