"""
Test runner for the AI Agent.
"""
import sys
import os

# Add the project root to Python path to fix import issues
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pytest

def run_unit_tests():
    """Run all unit tests."""
    print("🔷 Running unit tests")
    result = pytest.main(["-xvs", "tests/unit"])
    return result == 0

def run_integration_tests():
    """Run all integration tests."""
    print("\n🔷 Running integration tests")
    print("Note: The agent must be running for integration tests to pass")
    print("To start the agent: python src/main.py")
    
    # Check if agent is running
    import requests
    try:
        response = requests.get("http://localhost:8001/docs")
        if response.status_code == 200:
            print("✅ Agent is running")
        else:
            print("⚠️ Agent might not be running properly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Agent is not running! Please start it with: python src/main.py")
        return False
    
    # Run the tests
    result = pytest.main(["-xvs", "tests/integration"])
    return result == 0

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--unit-only":
        # Run only unit tests
        unit_result = run_unit_tests()
        success = unit_result
    elif len(sys.argv) > 1 and sys.argv[1] == "--integration-only":
        # Run only integration tests
        integration_result = run_integration_tests()
        success = integration_result
    else:
        # Run all tests
        unit_result = run_unit_tests()
        integration_result = run_integration_tests()
        success = unit_result and integration_result
    
    # Print summary
    print("\n🔶 Test Summary:")
    if "unit_result" in locals():
        print(f"Unit Tests: {'✅ Passed' if unit_result else '❌ Failed'}")
    if "integration_result" in locals():
        print(f"Integration Tests: {'✅ Passed' if integration_result else '❌ Failed'}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1) 