import pytest
import sys

if __name__ == "__main__":
    # Run all tests in the app/tests directory
    sys.exit(pytest.main(['-v', 'app/tests'])) 