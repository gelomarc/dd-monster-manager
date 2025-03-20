#!/usr/bin/env python
"""
Script to run all OCR tests.
This can be run with `python tests/run_ocr_tests.py` from the project root.
"""
import os
import sys
import unittest
import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == '__main__':
    print("====== Running OCR Unit Tests ======")
    # Run unittest-based tests
    unit_test_suite = unittest.defaultTestLoader.discover('app/tests', pattern='test_ocr_utils.py')
    unittest.TextTestRunner().run(unit_test_suite)
    
    print("\n====== Running OCR API Tests ======")
    # Run pytest-based tests
    pytest.main(['-xvs', 'app/tests/test_ocr_api.py'])
    
    print("\n====== Running OCR Client Tests ======")
    # Skip Selenium tests if appropriate
    if os.environ.get('SKIP_BROWSER_TESTS'):
        print("Skipping browser tests (SKIP_BROWSER_TESTS is set)")
    else:
        try:
            pytest.main(['-xvs', 'app/tests/test_ocr_client.py'])
        except Exception as e:
            print(f"Error running browser tests: {str(e)}")
    
    print("\nAll OCR tests completed!") 