import json
from mortgage_langgraph_agent import run_mortgage_analysis, interactive_mortgage_agent

def load_mortgage_data(filename: str) -> dict:
    """Load mortgage data"""
    try:
        with open(filename, 'r') as file:
            print(f" File {filename} loaded successfully")
            return json.load(file)
    except FileNotFoundError:
        print(f"❌ File {filename} not found")
        return None
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in {filename}")
        return None

def show_all_options(state):
    """Show all restructuring options with their descriptions from the JSON"""
    print("\n📋 ALL RESTRUCTURING OPTIONS FROM FILE:")
    print("=" * 60)
    
    options = state.get("restructure_options", [])
    if not options:
        print("❌ No restructuring options found in the data")
        return
    
    for i, option in enumerate(options, 1):
        print(f"\n{i}. {option.get('option_id', 'N/A')} - {option.get('loan_type', 'N/A')}")
        print(f"   📝 Description: {option.get('description', 'No description available')}")
        print(f"   ⏱️  Term: {option.get('term_months', 'N/A')} months ({option.get('term_months', 0)/12:.1f} years)")
        
        # Show additional fields if they exist
        if 'balance' in option:
            print(f"   💰 Balance: ${option['balance']:,.2f}")
        if 'rate' in option:
            print(f"   📊 Rate: {option['rate']}%")

    
    print("\n" + "=" * 60)

def demo_workflow_steps():
    """Demonstrate individual workflow steps"""

    
    from mortgage_langgraph_agent import (
        analyze_current_loans, 
        analyze_restructure_options, 
        compare_scenarios, 
        generate_comparisons
    )
    
    # Initialize state
    from mortgage_langgraph_agent import MortgageState
    from langchain.schema import SystemMessage
    
    state = {
        "messages": [SystemMessage(content="Home owner analyzing loan data.")],
        "current_loans": mortgage_data["existing_loans"],
        "restructure_options": mortgage_data["restructure_options"],
        "analysis_results": {},
        "comparisons": {},
        "user_goals": {"primary_goal": "monthly_savings"}
    }
    
    # Step 1: Analyze current loans
    print("\n Step 1️⃣: Analyzing Current Loans")
    state = analyze_current_loans(state)
    if "current_loans" in state["analysis_results"]:
        current = state["analysis_results"]["current_loans"]
        print(f"   ✅ Total Balance: ${current['total_balance']:,.2f}")
        print(f"   ✅ Monthly Payment: ${current['total_monthly_payment']:,.2f}")
    else:
        print("❌ No current loans found")

    print("\nStep 2️⃣ : Analyzing Restructuring Options")
    show_all_options(state) 
    state = analyze_restructure_options(state)     
    print("\nStep 3️⃣ : Comparing Scenarios")
    state = compare_scenarios(state)
    if "comparison" in state["analysis_results"]:
        comparison = state["analysis_results"]["comparison"]
        savings = comparison["savings"]["monthly"]
        print(f"   ✅ Monthly Savings: ${savings:,.2f}")
    
    # Step 4: Generate comparisons
    print("\n Step 4️⃣ : Generating comparisons")
    state = generate_comparisons(state)
    # Print the generated comparisons in a readable way
    if state["comparisons"] is not None:
        print("\n📝 Comparisons Analysis:")
        import json
        print(json.dumps(state["comparisons"], indent=2))

    else:
        print("❌ No comparisons analysis found.")

    
    print("\n✅ Demo completed! You can now run the interactive agent with:")
    print("python mortgage_langgraph_agent.py")
    exit()



if __name__ == "__main__":
    print("🏠 LangGraph Mortgage Agent Demo")
    print("=" * 40)
    print("Choose an option:")
    print("1. Run automated demos")
    print("2. Start interactive agent")
    print("3. Run demos + interactive agent")
    choice = input("\nEnter your choice (1, 2 or 3): ").strip()
    filename = input("Enter the filename of the mortgage data (or press Enter for default 'mortgage_data.json'): ").strip()
    if not filename:
        filename = "mortgage_data.json"
    mortgage_data = load_mortgage_data(filename)
    if choice == "1" or choice == "3":
        demo_workflow_steps()
    if choice == "2" or choice == "3":
        print("\n🚀 Starting Interactive Mortgage Agent...")
        interactive_mortgage_agent()
    else:
        print("❌ Invalid choice. Showing options...")
        mortgage_data = load_mortgage_data('mortgage_data.json')
        if mortgage_data:
            show_all_options(mortgage_data) 