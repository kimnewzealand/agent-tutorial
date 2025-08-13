import json
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from mortgage_langgraph_agent import (
    interactive_mortgage_agent,
    analyze_current_loans, 
    generate_comparisons
)
from langchain.schema import SystemMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# ============================================================================
# UTILITY FUNCTIONS (Lowest level - used by other functions)
# ============================================================================

def load_mortgage_data(filename: str) -> Optional[Dict[str, Any]]:
    """Load mortgage data from JSON file.
    
    Args:
        filename: Path to the JSON file containing mortgage data
        
    Returns:
        Dictionary containing mortgage data or None if loading fails
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    file_path = Path(filename)
    
    if not file_path.exists():
        logging.error(f"❌ Mortgage data file not found: {filename}")
        return None
    
    if not file_path.is_file():
        logging.error(f"❌ Path is not a file: {filename}")
        return None
    
    try:
        with file_path.open('r', encoding='utf-8') as file:
            data = json.load(file)
            logging.info(f"✅ Successfully loaded mortgage data from {filename}")
            return data
            
    except json.JSONDecodeError as e:
        logging.error(f"❌ Invalid JSON format in {filename}: {e}")
        return None
    except PermissionError:
        logging.error(f"❌ Permission denied accessing {filename}")
        return None
    except Exception as e:
        logging.error(f"❌ Unexpected error loading {filename}: {e}")
        return None

# ============================================================================
# CORE BUSINESS LOGIC (Middle level - main functionality)
# ============================================================================

def demo_workflow_steps(mortgage_data: Dict[str, Any]) -> None:
    """Demonstrate individual workflow steps with proper error handling.
    
    Args:
        mortgage_data: Dictionary containing mortgage data
        
    Returns:
        None
    """
    # Initialize state with proper validation
    try:
        state = {
            "messages": [SystemMessage(content="Home owner analyzing loan data.")],
            "current_loans": mortgage_data.get("existing_loans", []),
            "market_conditions": mortgage_data.get("market_conditions", {}),
            "user_goals": mortgage_data.get("user_goals", {}),
            "analysis_results": {},
            "comparisons": {},

        }
    except KeyError as e:
        logging.error(f"❌ Missing required data in mortgage_data: {e}")
        return
    
    # Step 1: Analyze current loans
    print("\n1️⃣ Step 1: Analyzing Current Loans")
    try:
        state = analyze_current_loans(state)
        if current_loans := state.get("analysis_results", {}).get("current_loans"):
            total_balance = current_loans['total_balance']
            total_monthly_payment = current_loans['total_monthly_payment']
            print(f"   ✅ Current Total Balance: ${total_balance:,.2f}")
            print(f"   ✅ Current Monthly Payment: ${total_monthly_payment:,.2f}")
        else:
            print("❌ No current loans found")
    except Exception as e:
        logging.error(f"❌ Error in step 1: {e}")

    
    # Step 2: Generate comparisons
    print("\n2️⃣ Step 2: Generating Comparisons")
    try:
        state = generate_comparisons(state)
        if comparisons := state.get("comparisons"):
            print("\n📝 Comparisons Analysis:")
            # Print the comparison analysis in a human-readable way
            analysis = comparisons.get('analysis')
            if hasattr(analysis, "content"):
                # If the analysis is an AIMessage or similar object
                print(analysis.content)
            elif isinstance(analysis, dict):
                # If the analysis is a dict, pretty print it
                import json
                print(json.dumps(analysis, indent=2))
            else:
                # Otherwise, just print as string
                print(str(analysis))
        else:
            print("❌ No comparisons analysis found.")
    except Exception as e:
        logging.error(f"❌ Error in step 3: {e}")

    print("\n✅ Demo completed! You can now run the interactive agent with:")
    print("python mortgage_langgraph_agent.py")

# ============================================================================
# USER INTERFACE FUNCTIONS (Higher level - user interaction)
# ============================================================================

def get_filename() -> str:
    """Get filename from user with default fallback.
    
    Returns:
        Filename as string
    """
    try:
        filename = input("Enter the filename of the mortgage data (or press Enter for default 'mortgage_data.json'): ").strip()
        return filename if filename else "mortgage_data.json"
    except (EOFError, KeyboardInterrupt):
        print("\n👋 Goodbye!")
        sys.exit(0)

def get_user_choice() -> str:
    """Get user choice for demo options.
    
    Returns:
        User's choice as a string
    """
    print("🏠 LangGraph Mortgage Agent Demo")
    print("=" * 40)
    print("Choose an option:")
    print("1. Run automated demos")
    print("2. Start interactive agent")
    print("3. Run demos + interactive agent")
    
    while True:
        try:
            choice = input("\nEnter your choice (1, 2, or 3): ").strip()
            if choice in {"1", "2", "3"}:
                return choice
            print("❌ Invalid choice. Please enter 1, 2, or 3.")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            sys.exit(0)

# ============================================================================
# MAIN FUNCTION (Entry point)
# ============================================================================

def main() -> None:
    """Main function to run the mortgage agent demo."""
    try:
        choice = get_user_choice()
        filename = get_filename()
        
        mortgage_data = load_mortgage_data(filename)
        if not mortgage_data:
            logging.error("❌ Failed to load mortgage data. Exiting.")
            return
        
        if choice in {"1", "3"}:
            demo_workflow_steps(mortgage_data)
        
        if choice in {"2", "3"}:
            print("\n🚀 Starting Interactive Mortgage Agent...")
            interactive_mortgage_agent()
            
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
