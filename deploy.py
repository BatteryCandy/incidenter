#!/usr/bin/env python3
"""
Incidenter Deployment Script

Simple deployment and package configuration for both CLI and web interfaces.
"""

import sys
import subprocess
import shutil
from pathlib import Path


def check_dependencies():
    """Check if all required dependencies are installed."""
    print("📦 Checking dependencies...")

    try:
        import flask  # noqa: F401
        import yaml  # noqa: F401
        import click  # noqa: F401
        import rich  # noqa: F401

        print("✅ All core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False


def validate_scenarios():
    """Validate all scenario files."""
    print("\n🔍 Validating scenarios...")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "cli.scenario_manager", "validate"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )

        if result.returncode == 0:
            print("✅ All scenarios validated successfully")
            return True
        else:
            print(f"❌ Scenario validation failed:\n{result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error validating scenarios: {e}")
        return False


def test_web_interface():
    """Run web interface tests."""
    print("\n🧪 Testing web interface...")

    try:
        result = subprocess.run(
            [sys.executable, "tests/test_web_interface.py"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )

        if result.returncode == 0:
            print("✅ Web interface tests passed")
            return True
        else:
            print(f"❌ Web interface tests failed:\n{result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running web tests: {e}")
        return False


def create_package():
    """Create a deployable package."""
    print("\n📦 Creating deployment package...")

    package_dir = Path("dist/incidenter")
    package_dir.mkdir(parents=True, exist_ok=True)

    # Copy essential files
    essential_dirs = ["cli", "server", "scenarios", "facilitator", "utils", "scoring"]
    essential_files = [
        "requirements.txt",
        "README.md",
        "WEB_INTERFACE_GUIDE.md",
        "incidenter.py",
    ]

    for dir_name in essential_dirs:
        if Path(dir_name).exists():
            shutil.copytree(dir_name, package_dir / dir_name, dirs_exist_ok=True)

    for file_name in essential_files:
        if Path(file_name).exists():
            shutil.copy2(file_name, package_dir / file_name)

    # Create startup scripts
    create_startup_scripts(package_dir)

    print(f"✅ Package created at: {package_dir.absolute()}")
    return package_dir


def create_startup_scripts(package_dir):
    """Create convenient startup scripts."""

    # CLI startup script
    cli_script = package_dir / "start_cli.py"
    cli_script.write_text(
        """#!/usr/bin/env python3
'''Incidenter CLI Launcher'''

import sys
import subprocess
from pathlib import Path

def main():
    # Change to script directory
    script_dir = Path(__file__).parent

    print("🎮 Incidenter CLI Interface")
    print("Available commands:")
    print("  list-scenarios    - Show all available scenarios")
    print("  validate         - Validate all scenario files")
    print("  stats           - Show scenario statistics")
    print("  play            - Start interactive CLI game")
    print()

    if len(sys.argv) == 1:
        # Interactive mode
        while True:
            try:
                cmd = input("incidenter> ").strip()
                if not cmd:
                    continue
                if cmd in ['exit', 'quit']:
                    break

                if cmd == 'list-scenarios':
                    subprocess.run([
                        sys.executable, "-m", "cli.scenario_manager",
                        "list-scenarios"
                    ], cwd=script_dir)
                elif cmd == 'validate':
                    subprocess.run([
                        sys.executable, "-m", "cli.scenario_manager", "validate"
                    ], cwd=script_dir)
                elif cmd == 'stats':
                    subprocess.run([
                        sys.executable, "-m", "cli.scenario_manager", "stats"
                    ], cwd=script_dir)
                elif cmd.startswith('play'):
                    parts = cmd.split()
                    if len(parts) > 1:
                        scenario = parts[1]
                        subprocess.run([
                            sys.executable, "incidenter.py", "play",
                            "--scenario", scenario
                        ], cwd=script_dir)
                    else:
                        print("Usage: play <scenario_file>")
                else:
                    print(f"Unknown command: {cmd}")
            except KeyboardInterrupt:
                break
            except EOFError:
                break
    else:
        # Pass through to main CLI
        subprocess.run([sys.executable] + sys.argv[1:], cwd=script_dir)

if __name__ == "__main__":
    main()
"""
    )

    # Web startup script
    web_script = package_dir / "start_web.py"
    web_script.write_text(
        """#!/usr/bin/env python3
'''Incidenter Web Interface Launcher'''

import sys
import subprocess
import webbrowser
import time
from pathlib import Path
from threading import Timer

def open_browser():
    '''Open browser after short delay'''
    time.sleep(2)
    webbrowser.open('http://localhost:5003')

def main():
    script_dir = Path(__file__).parent

    print("🌐 Starting Incidenter Web Interface...")
    print("Web server will be available at: http://localhost:5003")
    print("Press Ctrl+C to stop the server")

    # Open browser after delay
    Timer(2.0, open_browser).start()

    try:
        subprocess.run([sys.executable, "server/app.py"], cwd=script_dir)
    except KeyboardInterrupt:
        print("\\n👋 Shutting down web server...")

if __name__ == "__main__":
    main()
"""
    )

    # Make scripts executable
    cli_script.chmod(0o755)
    web_script.chmod(0o755)

    # Create batch files for Windows
    if sys.platform.startswith("win"):
        (package_dir / "start_cli.bat").write_text("@echo off\\npython start_cli.py %*")
        (package_dir / "start_web.bat").write_text("@echo off\\npython start_web.py %*")


def print_deployment_info(package_dir):
    """Print deployment instructions."""
    print(
        f"""
🚀 Incidenter Deployment Complete!

Package Location: {package_dir.absolute()}

Quick Start:
  CLI Interface:  python start_cli.py
  Web Interface:  python start_web.py

Installation:
  1. Copy the dist/incidenter folder to your target system
  2. Install dependencies: pip install -r requirements.txt
  3. Run either interface using the startup scripts

Features:
  ✅ 8 Historical cybersecurity scenarios
  ✅ CLI and web interfaces
  ✅ AI facilitator with fallback responses
  ✅ Session management and progress tracking
  ✅ Comprehensive scenario validation
  ✅ Modern responsive web design

For detailed setup instructions, see README.md and WEB_INTERFACE_GUIDE.md
"""
    )


def main():
    """Main deployment function."""
    print("🎮 Incidenter Deployment Script")
    print("=" * 50)

    # Pre-deployment checks
    if not check_dependencies():
        sys.exit(1)

    if not validate_scenarios():
        print("⚠️  Warning: Some scenarios failed validation")
        response = input("Continue deployment? (y/N): ")
        if response.lower() != "y":
            sys.exit(1)

    if not test_web_interface():
        print("⚠️  Warning: Web interface tests failed")
        response = input("Continue deployment? (y/N): ")
        if response.lower() != "y":
            sys.exit(1)

    # Create deployment package
    package_dir = create_package()

    # Show deployment info
    print_deployment_info(package_dir)


if __name__ == "__main__":
    main()
