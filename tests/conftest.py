"""
Pytest configuration and shared fixtures.
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set a dummy GROQ_API_KEY for tests if not already set
os.environ.setdefault("GROQ_API_KEY", "test-dummy-key-for-testing")


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return {
        "api_url": "http://localhost:8000",
        "test_timeout": 30
    }
