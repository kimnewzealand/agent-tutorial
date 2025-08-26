import streamlit as st
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
import sys
import os

# Add the current directory to Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mortgage_langgraph_agent import (
    analyze_current_loans,
    generate_comparisons
)
from langchain.schema import SystemMessage

def configure_streamlit_page():
    """Configure Streamlit page settings - only call when in Streamlit context."""
    st.set_page_config(
        page_title="🏠 Mortgage Restructuring Agent",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

def load_mortgage_data(filename: str) -> Optional[Dict[str, Any]]:
    """Load mortgage data from JSON file."""
    file_path = Path(filename)
    
    if not file_path.exists():
        st.error(f"❌ Mortgage data file not found: {filename}")
        return None
    
    try:
        with file_path.open('r', encoding='utf-8') as file:
            data = json.load(file)
            st.success(f"✅ Successfully loaded mortgage data from {filename}")
            return data
    except json.JSONDecodeError as e:
        st.error(f"❌ Invalid JSON format in {filename}: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error loading {filename}: {e}")
        return None

def display_current_loans(loans_data: list):
    """Display current loans in a nice format."""
    if not loans_data:
        st.warning("No current loans found.")
        return
    
    st.subheader("📋 Current Loans")
    
    # Create DataFrame for better display
    loans_df = pd.DataFrame(loans_data)
    
    # Display as a table
    st.dataframe(
        loans_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Calculate totals
    total_balance = sum(loan.get('balance', 0) for loan in loans_data)
    total_monthly_payment = sum(loan.get('monthly_payment', 0) for loan in loans_data)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("�� Total Balance", f"${total_balance:,.2f}")
    with col2:
        st.metric("💳 Monthly Payment", f"${total_monthly_payment:,.2f}")
    with col3:
        avg_rate = sum(loan.get('rate', 0) * loan.get('balance', 0) for loan in loans_data) / total_balance if total_balance > 0 else 0
        st.metric("📊 Weighted Avg Rate", f"{avg_rate:.3f}%")

def display_restructure_options(options_data: list):
    """Display restructuring options."""
    if not options_data:
        st.warning("No restructuring options found.")
        return
    
    st.subheader("🔄 Restructuring Options")
    
    # Create DataFrame
    options_df = pd.DataFrame(options_data)
    
    # Display as a table
    st.dataframe(
        options_df,
        use_container_width=True,
        hide_index=True
    )

def run_analysis(mortgage_data: Dict[str, Any], user_goals: Dict[str, Any]):
    """Run the mortgage analysis workflow."""
    try:
        # Initialize state
        state = {
            "messages": [SystemMessage(content="Home owner analyzing loan data.")],
            "current_loans": mortgage_data.get("existing_loans", []),
            "market_conditions": mortgage_data.get("market_conditions", {}),
            "user_goals": user_goals,
            "analysis_results": {},
            "comparisons": {}
        }
        
        # Step 1: Analyze current loans
        with st.spinner("🔍 Analyzing current loans..."):
            state = analyze_current_loans(state)
        
        if "current_loans" in state.get("analysis_results", {}):
            current_loans = state["analysis_results"]["current_loans"]
            st.success(f"✅ Analysis complete! Total balance: ${current_loans.get('total_balance', 0):,.2f}")
        
        # Step 2: Generate comparisons
        with st.spinner("🤖 Generating personalized comparisons..."):
            state = generate_comparisons(state)
        
        if "comparisons" in state and state["comparisons"]:
            st.success("✅ Comparisons generated successfully!")
            return state
        
        return None
        
    except Exception as e:
        st.error(f"❌ Error during analysis: {e}")
        return None

def main():
    # Configure Streamlit page (only when in proper context)
    try:
        configure_streamlit_page()
    except Exception:
        # If page config fails, continue without it
        pass

    # Main header
    st.markdown('<h1 class="main-header">🏠 Mortgage Restructuring Agent</h1>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # File selection
        file_option = st.selectbox(
            "Choose mortgage data file:",
            ["mortgage_data.json", "mortgage_data_private.json"],
            index=0
        )
        
        # User goals
        st.subheader("🎯 Your Goals")
        primary_goal = st.selectbox(
            "Primary Goal:",
            ["monthly_savings", "total_savings", "equity_building", "risk_reduction"],
            format_func=lambda x: x.replace("_", " ").title()
        )
        
        risk_tolerance = st.selectbox(
            "Risk Tolerance:",
            ["low", "moderate", "high"],
            format_func=lambda x: x.title()
        )
        
        time_horizon = st.selectbox(
            "Time Horizon:",
            ["short_term", "medium_term", "long_term"],
            format_func=lambda x: x.replace("_", " ").title()
        )
        
        additional_notes = st.text_area(
            "Additional Considerations:",
            placeholder="Any specific requirements or preferences..."
        )
        
        # Analysis button
        if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
            st.session_state.run_analysis = True
    
    # Main content area
    if 'run_analysis' not in st.session_state:
        st.session_state.run_analysis = False
    
    if st.session_state.run_analysis:
        # Load data
        mortgage_data = load_mortgage_data(file_option)
        
        if mortgage_data:
            # Display current loans
            display_current_loans(mortgage_data.get("existing_loans", []))
            
            # Display restructuring options
            display_restructure_options(mortgage_data.get("restructure_options", []))
            
            # Prepare user goals
            user_goals = {
                "primary_goal": primary_goal,
                "risk_tolerance": risk_tolerance,
                "time_horizon": time_horizon,
                "additional_considerations": additional_notes
            }
            
            # Run analysis
            result = run_analysis(mortgage_data, user_goals)
            
            if result and "comparisons" in result:
                st.subheader("💡 AI-Generated Comparisons")
                
                # Display the analysis
                if "analysis" in result["comparisons"]:
                    analysis_content = result["comparisons"]["analysis"]
                    
                    # Try to extract content if it's an AIMessage
                    if hasattr(analysis_content, 'content'):
                        analysis_text = analysis_content.content
                    else:
                        analysis_text = str(analysis_content)
                    
                    st.markdown(analysis_text)
                else:
                    st.info("Analysis completed but no detailed comparisons available.")
            
            # Reset analysis flag
            st.session_state.run_analysis = False
            
            # Add a button to run another analysis
            if st.button("🔄 Run Another Analysis"):
                st.session_state.run_analysis = True
                st.rerun()
    
    else:
        # Welcome message and instructions
        st.markdown("""
        ## 🎯 Welcome to the Mortgage Restructuring Agent!
        
        This AI-powered tool helps you analyze your mortgage options and find the best restructuring strategy.
        
        ### 📋 What you can do:
        - **Analyze Current Loans**: Get a detailed breakdown of your existing mortgage situation
        - **Compare Options**: See how different restructuring options stack up
        - **AI Recommendations**: Get personalized advice based on your goals and risk tolerance
        
        ### �� How to get started:
        1. **Configure your preferences** in the sidebar
        2. **Choose your mortgage data file**
        3. **Set your financial goals**
        4. **Click "Run Analysis"** to get started
        
        ### 💡 Tips for best results:
        - Be specific about your goals
        - Consider your risk tolerance
        - Think about your time horizon
        - Add any special considerations in the notes
        """)
        
        # Quick demo section
        with st.expander("🎬 Quick Demo - See what the analysis looks like"):
            st.markdown("""
            **Sample Analysis Output:**
            
            Based on your current mortgage situation and goals, here are the key recommendations:
            
            **Current Situation:**
            - Total Balance: $10,000
            - Monthly Payment: $1,000
            - Average Rate: 3%
            
            **Recommended Strategy:**
            1. **Conservative Approach**: Consider a 24-month fixed rate to reduce monthly payments
            2. **Risk Management**: Lock in current favorable rates
            3. **Savings Potential**: $703/month in immediate savings
            
            **Next Steps:**
            - Review closing costs vs. monthly savings
            - Consider break-even timeline
            - Consult with your mortgage advisor
            """)

# Only run main() when executed as a Streamlit app
if __name__ == "__main__":
    # Check if we're running in Streamlit context
    try:
        # This will only work if we're in a Streamlit context
        import streamlit.runtime.scriptrunner as scriptrunner
        if scriptrunner.get_script_run_ctx() is not None:
            main()
        else:
            # Running outside Streamlit context (e.g., direct Python execution)
            print("This script is designed to run with Streamlit.")
            print("Please run: streamlit run mortgage_web_demo.py")
    except (ImportError, AttributeError):
        # Fallback for older Streamlit versions or when not in Streamlit context
        try:
            import streamlit as st
            # Try to access Streamlit's session state to check if we're in context
            _ = st.session_state
            main()
        except Exception:
            print("This script is designed to run with Streamlit.")
            print("Please run: streamlit run mortgage_web_demo.py")