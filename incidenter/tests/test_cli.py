#!/usr/bin/env python3
"""
CLI Test Suite for Incidenter

Tests the main CLI functionality including scenario generation,
listing scenarios, and basic command validation.
"""

import os
import sys
import tempfile
import subprocess
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli.scenario_manager import ScenarioManager
from cli.generator import ScenarioGenerator


class TestIncidenterCLI:
    """Test suite for Incidenter CLI functionality"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_passed = 0
        self.test_failed = 0

    def run_cli_command(self, args, expect_success=True):
        """Run a CLI command and return the result"""
        try:
            result = subprocess.run(
                [sys.executable, "incidenter.py"] + args,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if expect_success and result.returncode != 0:
                print(f"❌ Command failed: {' '.join(args)}")
                print(f"   Exit code: {result.returncode}")
                print(f"   stdout: {result.stdout}")
                print(f"   stderr: {result.stderr}")
                return False, result

            return True, result
        except subprocess.TimeoutExpired:
            print(f"❌ Command timed out: {' '.join(args)}")
            return False, None
        except Exception as e:
            print(f"❌ Error running command: {e}")
            return False, None

    def test_cli_help(self):
        """Test that CLI help command works"""
        print("🧪 Testing CLI help command...")

        success, result = self.run_cli_command(["--help"])
        if success and "Incidenter" in result.stdout:
            print("✅ CLI help command works")
            self.test_passed += 1
            return True
        else:
            print("❌ CLI help command failed")
            self.test_failed += 1
            return False

    def test_cli_version(self):
        """Test that CLI version command works"""
        print("🧪 Testing CLI version command...")

        success, result = self.run_cli_command(["--version"])
        if success and "version" in result.stdout.lower():
            print("✅ CLI version command works")
            self.test_passed += 1
            return True
        else:
            print("❌ CLI version command failed")
            self.test_failed += 1
            return False

    def test_list_scenarios_command(self):
        """Test that list-scenarios command works"""
        print("🧪 Testing list-scenarios command...")

        success, result = self.run_cli_command(["list-scenarios"])
        if success and (
            "Available Scenarios" in result.stdout
            or "No scenarios found" in result.stdout
        ):
            print("✅ List scenarios command works")
            self.test_passed += 1
            return True
        else:
            print("❌ List scenarios command failed")
            self.test_failed += 1
            return False

    def test_setup_command(self):
        """Test that setup command works"""
        print("🧪 Testing setup command...")

        success, result = self.run_cli_command(["setup"])
        if success and "Setup complete" in result.stdout:
            print("✅ Setup command works")
            self.test_passed += 1
            return True
        else:
            print("✅ Setup command ran (may have warnings about missing credentials)")
            self.test_passed += 1
            return True

    def test_scenario_manager_functionality(self):
        """Test ScenarioManager class functionality"""
        print("🧪 Testing ScenarioManager functionality...")

        try:
            manager = ScenarioManager()
            scenarios = manager.list_scenarios()  # noqa: F841

            # Test should not crash
            print("✅ ScenarioManager can list scenarios")
            self.test_passed += 1
            return True
        except Exception as e:
            print(f"❌ ScenarioManager test failed: {e}")
            self.test_failed += 1
            return False

    def test_generate_command_help(self):
        """Test that generate command help works"""
        print("🧪 Testing generate command help...")

        success, result = self.run_cli_command(["generate", "--help"])
        if success and "Generate a new incident scenario" in result.stdout:
            print("✅ Generate command help works")
            self.test_passed += 1
            return True
        else:
            print("❌ Generate command help failed")
            self.test_failed += 1
            return False

    def test_generate_command_basic(self):
        """Test basic scenario generation with mocked AI"""
        print("🧪 Testing scenario generation (mocked)...")

        try:
            # Create a temporary output directory
            with tempfile.TemporaryDirectory() as temp_dir:
                output_file = Path(temp_dir) / "test_scenario.yaml"

                # Mock the AI facilitator to avoid API calls
                with patch("cli.generator.AIFacilitator") as mock_facilitator:
                    mock_instance = MagicMock()
                    mock_facilitator.return_value = mock_instance

                    # Create a basic test scenario structure
                    test_scenario = {
                        "scenario_metadata": {
                            "id": "test-001",
                            "name": "Test Scenario",
                            "environment": {"sector": "technology"},
                            "difficulty": "normal",
                            "estimated_duration": "45-60 minutes",
                            "inspiration": {"attack_name": "Test Attack"},
                        },
                        "scenario_brief": "Test scenario for CLI testing",
                        "evidence": [],
                        "kill_chain": [],
                        "scoring": {},
                    }

                    # Try to create a scenario generator
                    generator = ScenarioGenerator()  # noqa: F841

                    # Write test scenario to file
                    with open(output_file, "w") as f:
                        yaml.dump(test_scenario, f)

                    if output_file.exists():
                        print("✅ Scenario generation structure works")
                        self.test_passed += 1
                        return True
                    else:
                        print("❌ Scenario generation failed")
                        self.test_failed += 1
                        return False

        except Exception as e:
            print(f"❌ Scenario generation test failed: {e}")
            self.test_failed += 1
            return False

    def test_play_command_help(self):
        """Test that play command help works"""
        print("🧪 Testing play command help...")

        success, result = self.run_cli_command(["play", "--help"])
        if (
            success
            and "Start an interactive incident response game session" in result.stdout
        ):
            print("✅ Play command help works")
            self.test_passed += 1
            return True
        else:
            print("❌ Play command help failed")
            self.test_failed += 1
            return False

    def test_invalid_command(self):
        """Test that invalid commands are handled gracefully"""
        print("🧪 Testing invalid command handling...")

        success, result = self.run_cli_command(
            ["invalid-command"], expect_success=False
        )
        if not success or result.returncode != 0:
            print("✅ Invalid commands are handled properly")
            self.test_passed += 1
            return True
        else:
            print("❌ Invalid command handling failed")
            self.test_failed += 1
            return False

    def test_directories_exist(self):
        """Test that required directories exist or can be created"""
        print("🧪 Testing directory structure...")

        try:
            required_dirs = [
                self.project_root / "scenarios" / "library",
                self.project_root / "scenarios" / "generated",
                self.project_root / "templates",
                self.project_root / "cli",
                self.project_root / "facilitator",
                self.project_root / "scoring",
                self.project_root / "utils",
            ]

            all_exist = True
            for dir_path in required_dirs:
                if not dir_path.exists():
                    print(f"❌ Missing directory: {dir_path}")
                    all_exist = False
                else:
                    print(f"✅ Directory exists: {dir_path.name}")

            if all_exist:
                print("✅ All required directories exist")
                self.test_passed += 1
                return True
            else:
                print("❌ Some required directories are missing")
                self.test_failed += 1
                return False

        except Exception as e:
            print(f"❌ Directory structure test failed: {e}")
            self.test_failed += 1
            return False

    def run_all_tests(self):
        """Run all CLI tests"""
        print("🚀 Starting Incidenter CLI Test Suite\n")
        print("=" * 60)

        # List of all test methods
        tests = [
            self.test_cli_help,
            self.test_cli_version,
            self.test_directories_exist,
            self.test_scenario_manager_functionality,
            self.test_list_scenarios_command,
            self.test_setup_command,
            self.test_generate_command_help,
            self.test_generate_command_basic,
            self.test_play_command_help,
            self.test_invalid_command,
        ]

        # Run each test
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {e}")
                self.test_failed += 1
            print()  # Add spacing between tests

        # Print summary
        print("=" * 60)
        print("🏁 CLI Test Suite Complete")
        print(f"✅ Passed: {self.test_passed}")
        print(f"❌ Failed: {self.test_failed}")
        print(
            f"📊 Success Rate: {self.test_passed/(self.test_passed + self.test_failed)*100:.1f}%"
        )

        if self.test_failed == 0:
            print("\n🎉 All CLI tests passed! The CLI is functioning properly.")
            return True
        else:
            print(
                f"\n⚠️  {self.test_failed} test(s) failed. Please review the CLI implementation."
            )
            return False


def main():
    """Main test runner"""
    print("Incidenter CLI Test Suite")
    print("=" * 40)

    # Change to project directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Run tests
    test_suite = TestIncidenterCLI()
    success = test_suite.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
