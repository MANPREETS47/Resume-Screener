"""
Quick start helper script.
Run tests, start server, or check installation.
"""

import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command with error handling."""
    print(f"\n{'='*60}")
    print(f"📌 {description}")
    print(f"{'='*60}")
    print(f"$ {cmd}\n")
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def main():
    """Main entry point."""
    root_dir = Path(__file__).parent
    
    if len(sys.argv) < 2:
        print("""
Resume Screener API - Quick Start Helper

Usage:
  python quickstart.py <command>

Commands:
  install     - Install all dependencies
  dev-install - Install with development tools
  test        - Run all tests
  test-unit   - Run unit tests only
  test-cov    - Run tests with coverage report
  server      - Start development server
  lint        - Run code linting
  format      - Format code with black
  clean       - Remove cache and temp files
  help        - Show this help message

Examples:
  python quickstart.py install
  python quickstart.py test
  python quickstart.py server
        """)
        return
    
    command = sys.argv[1]
    
    if command == "install":
        run_command("pip install -r requirements.txt", "Installing dependencies")
    
    elif command == "dev-install":
        run_command("pip install -r requirements.txt", "Installing dependencies")
        run_command("pip install -e .", "Installing in development mode")
    
    elif command == "test":
        run_command("pytest", "Running all tests")
    
    elif command == "test-unit":
        run_command("pytest tests/unit/ -v", "Running unit tests")
    
    elif command == "test-cov":
        run_command("pytest --cov=src --cov-report=html", "Running tests with coverage")
    
    elif command == "server":
        run_command(
            "python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000",
            "Starting development server"
        )
    
    elif command == "lint":
        run_command("flake8 src tests", "Running flake8 linter")
        run_command("mypy src", "Running mypy type checker")
    
    elif command == "format":
        run_command("black src tests", "Formatting code with black")
    
    elif command == "clean":
        import shutil
        print("\\n" + "="*60)
        print("🧹 Cleaning cache and temporary files")
        print("="*60)
        
        patterns = [
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            "*.pyc",
            ".coverage",
            "htmlcov"
        ]
        
        for pattern in patterns:
            for item in root_dir.rglob(pattern):
                if item.is_file():
                    item.unlink()
                    print(f"Removed: {item}")
                elif item.is_dir():
                    shutil.rmtree(item)
                    print(f"Removed: {item}/")
    
    elif command in ["help", "-h", "--help"]:
        print(__doc__)
    
    else:
        print(f"Unknown command: {command}")
        print("Use 'python quickstart.py help' for available commands")
        sys.exit(1)

if __name__ == "__main__":
    main()
