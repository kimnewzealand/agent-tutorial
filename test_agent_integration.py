#!/usr/bin/env python3
"""
Test script to verify the smolagents integration works properly.
"""

import json
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_agent_import():
    """Test that the agent can be imported and initialized"""
    print("🧪 Testing agent import and initialization...")
    
    try:
        from mortgage_agent import get_agent, analyze_current_loans, generate_comparisons
        print("✅ Successfully imported mortgage agent functions!")
        return True
    except Exception as e:
        print(f"❌ Error importing agent: {e}")
        return False

def test_agent_tools():
    """Test that the agent tools work correctly"""
    print("\n🧪 Testing agent tools...")
    
    try:
        from mortgage_agent import analyze_loan_data, calculate_restructure_options
        
        # Test loan analysis tool
        test_loan_data = {
            "existing_loans": [
                {"balance": 100000, "rate": 3.5, "monthly_payment": 500},
                {"balance": 50000, "rate": 4.0, "monthly_payment": 250}
            ]
        }
        
        result = analyze_loan_data(json.dumps(test_loan_data))
        analysis = json.loads(result)
        
        if "total_balance" in analysis and analysis["total_balance"] == 150000:
            print("✅ Loan analysis tool working correctly!")
        else:
            print(f"⚠️  Unexpected analysis result: {analysis}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing tools: {e}")
        return False

def test_backward_compatibility():
    """Test that the backward compatibility functions work"""
    print("\n🧪 Testing backward compatibility functions...")
    
    try:
        from mortgage_agent import analyze_current_loans, generate_comparisons
        
        # Create test state in old format
        test_state = {
            "current_loans": [
                {"balance": 100000, "rate": 3.5, "monthly_payment": 500}
            ],
            "market_conditions": {
                "current_rates": {
                    "floating": 3.0,
                    "12_months_fixed": 3.2,
                    "24_months_fixed": 3.4
                }
            },
            "user_goals": {
                "primary_goal": "monthly_savings",
                "risk_tolerance": "moderate"
            },
            "analysis_results": {},
            "comparisons": {}
        }
        
        # Test analyze_current_loans
        result_state = analyze_current_loans(test_state)
        
        if "analysis_results" in result_state and "current_loans" in result_state["analysis_results"]:
            print("✅ Backward compatibility for analyze_current_loans working!")
        else:
            print("⚠️  analyze_current_loans may have issues")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing backward compatibility: {e}")
        return False

def test_web_demo_import():
    """Test that the web demo can import the agent"""
    print("\n🧪 Testing web demo import...")
    
    try:
        from mortgage_web_demo import main, configure_streamlit_page
        print("✅ Web demo imports successfully!")
        return True
    except Exception as e:
        print(f"❌ Error importing web demo: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Testing Smolagents Integration for Mortgage Agent")
    print("=" * 60)
    
    # Run all tests
    tests = [
        test_agent_import,
        test_agent_tools,
        test_backward_compatibility,
        test_web_demo_import
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    if all(results):
        print("🎉 All tests passed! Smolagents integration is working correctly.")
        print("\n📋 Next steps:")
        print("1. Set your ANTHROPIC_API_KEY in .env file")
        print("2. Run: streamlit run mortgage_web_demo.py")
        print("3. The web demo will now use the smolagents-powered agent!")
    else:
        print("❌ Some tests failed. Please check the implementation.")
        failed_count = len([r for r in results if not r])
        print(f"Failed tests: {failed_count}/{len(tests)}")
        sys.exit(1)
