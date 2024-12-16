import pytest
import sys
import os

def main():
    """Run all tests"""
    # Add project root to Python path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    # Run tests
    pytest.main(['-v', '--tb=short'])

if __name__ == '__main__':
    main() 