import os
import json
import pandas as pd
from typing import TypedDict, Annotated, Sequence
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from datetime import datetime

load_dotenv()

# State definition for the mortgage workflow
class MortgageState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    current_loans: Annotated[dict, "Current mortgage loan data"]
    restructure_options: Annotated[dict, "Available restructuring options"]
    analysis_results: Annotated[dict, "Analysis results from tools"]
    comparisons: Annotated[dict, "Final comparisons"]
    user_goals: Annotated[dict, "User's financial goals and preferences"]

# Tool definitions
class LoanAnalysisInput(BaseModel):
    loan_data: str = Field(description="JSON string containing existing loan information")

class LoanAnalysisTool(BaseTool):
    name: str = "loan_analysis"
    description: str = "Analyze existing mortgage loans and calculate current payment obligations"
    args_schema: type[BaseModel] = LoanAnalysisInput
    
    def _run(self, loan_data: str) -> str:
        """Analyze existing loans and provide current financial summary"""
        try:
            loans = json.loads(loan_data)
            total_balance = sum(loan['balance'] for loan in loans['existing_loans'])
            total_monthly_payment = sum(loan['monthly_payment'] for loan in loans['existing_loans'])
            weighted_rate = sum(loan['balance'] * loan['rate'] for loan in loans['existing_loans']) / total_balance
            
            analysis = {
                "total_balance": total_balance,
                "total_monthly_payment": total_monthly_payment,
                "weighted_average_rate": weighted_rate,
                "loan_count": len(loans['existing_loans']),
                "loans": loans['existing_loans']
            }
            
            return json.dumps(analysis)
        except Exception as e:
            return json.dumps({"error": f"Error analyzing loan data: {e}"})

class RestructureOptionsInput(BaseModel):
    options_data: str = Field(description="JSON string containing restructuring options")

class RestructureOptionsTool(BaseTool):
    name: str = "restructure_options"
    description: str = "Analyze available restructuring options and calculate potential savings"
    args_schema: type[BaseModel] = RestructureOptionsInput
    
    def _run(self, options_data: str) -> str:
        """Analyze restructuring options and calculate potential benefits"""
        try:
            options = json.loads(options_data)
            analyzed_options = []
            
            for option in options['restructure_options']:
                monthly_payment = self._calculate_monthly_payment(
                    option['balance'], 
                    option['rate'], 
                    option['term_years']
                )
                total_interest = (monthly_payment * option['term_years'] * 12) - option['balance']
                
                analyzed_option = {
                    **option,
                    "monthly_payment": monthly_payment,
                    "total_interest": total_interest,
                    "total_cost": total_interest + option['balance']
                }
                analyzed_options.append(analyzed_option)
            
            return json.dumps({"restructure_options": analyzed_options})
        except Exception as e:
            return json.dumps({"error": f"Error analyzing options: {e}"})
    
    def _calculate_monthly_payment(self, principal: float, rate: float, years: int) -> float:
        """Calculate monthly mortgage payment"""
        monthly_rate = rate / 100 / 12
        num_payments = years * 12
        if monthly_rate == 0:
            return principal / num_payments
        return principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

class ComparisonInput(BaseModel):
    comparison_data: str = Field(description="JSON string containing current vs proposed loan scenarios")

class ComparisonTool(BaseTool):
    name: str = "comparison"
    description: str = "Compare current loan situation with proposed restructuring options"
    args_schema: type[BaseModel] = ComparisonInput
    
    def _run(self, comparison_data: str) -> str:
        """Compare current loans with restructuring options"""
        try:
            data = json.loads(comparison_data)
            
            # Calculate current totals
            current_total_payment = sum(loan['monthly_payment'] for loan in data['current_loans'])
            current_total_balance = sum(loan['balance'] for loan in data['current_loans'])
            
            # Calculate proposed totals
            proposed_total_payment = sum(option['monthly_payment'] for option in data['proposed_options'])
            proposed_total_balance = sum(option['balance'] for option in data['proposed_options'])
            
            monthly_savings = current_total_payment - proposed_total_payment
            annual_savings = monthly_savings * 12
            
            comparison = {
                "current": {
                    "total_balance": current_total_balance,
                    "total_monthly_payment": current_total_payment
                },
                "proposed": {
                    "total_balance": proposed_total_balance,
                    "total_monthly_payment": proposed_total_payment
                },
                "savings": {
                    "monthly": monthly_savings,
                    "annual": annual_savings,
                    "total_30_years": annual_savings * 30
                }
            }
            
            return json.dumps(comparison)
        except Exception as e:
            return json.dumps({"error": f"Error in comparison: {e}"})

class BreakEvenInput(BaseModel):
    break_even_data: str = Field(description="JSON string containing closing costs and monthly savings")

class BreakEvenTool(BaseTool):
    name: str = "break_even_analysis"
    description: str = "Calculate break-even point for refinancing based on closing costs and monthly savings"
    args_schema: type[BaseModel] = BreakEvenInput
    
    def _run(self, break_even_data: str) -> str:
        """Calculate break-even analysis"""
        try:
            data = json.loads(break_even_data)
            closing_costs = data['closing_costs']
            monthly_savings = data['monthly_savings']
            
            if monthly_savings <= 0:
                return json.dumps({"error": "No monthly savings to calculate break-even"})
            
            break_even_months = closing_costs / monthly_savings
            break_even_years = break_even_months / 12
            
            analysis = {
                "closing_costs": closing_costs,
                "monthly_savings": monthly_savings,
                "break_even_months": break_even_months,
                "break_even_years": break_even_years,
                "profitable_after": f"{break_even_months:.1f} months ({break_even_years:.1f} years)"
            }
            
            return json.dumps(analysis)
        except Exception as e:
            return json.dumps({"error": f"Error in break-even analysis: {e}"})

# Node functions for the workflow
def analyze_current_loans(state: MortgageState) -> MortgageState:
    """Analyze current mortgage loans"""
    try:
        tool = LoanAnalysisTool()
        loan_data = json.dumps({"existing_loans": state["current_loans"]})
        result = tool._run(loan_data)
        
        state["analysis_results"]["current_loans"] = json.loads(result)
        
        # Add analysis message
        analysis_msg = f"Current loan analysis completed. Total balance: ${state['analysis_results']['current_loans']['total_balance']:,.2f}"
        state["messages"].append(AIMessage(content=analysis_msg))
        
    except Exception as e:
        state["messages"].append(AIMessage(content=f"Error analyzing current loans: {e}"))
    
    return state

def analyze_restructure_options(state: MortgageState) -> MortgageState:
    """Analyze restructuring options"""
    try:
        tool = RestructureOptionsTool()
        options_data = json.dumps({"restructure_options": state["restructure_options"]})
        result = tool._run(options_data)
        
        state["analysis_results"]["restructure_options"] = json.loads(result)
        
        # Add analysis message
        options_count = len(state["analysis_results"]["restructure_options"]["restructure_options"])
        analysis_msg = f"Restructuring options analysis completed. {options_count} options analyzed."
        state["messages"].append(AIMessage(content=analysis_msg))
        
    except Exception as e:
        state["messages"].append(AIMessage(content=f"Error analyzing restructuring options: {e}"))
    
    return state

def compare_scenarios(state: MortgageState) -> MortgageState:
    """Compare current vs proposed scenarios"""
    try:
        tool = ComparisonTool()
        
        # Get current loans and first restructuring option for comparison
        current_loans = state["current_loans"]
        first_option = state["analysis_results"]["restructure_options"]["restructure_options"][0]
        
        comparison_data = json.dumps({
            "current_loans": current_loans,
            "proposed_options": [first_option]
        })
        
        result = tool._run(comparison_data)
        state["analysis_results"]["comparison"] = json.loads(result)
        
        # Add comparison message
        savings = state["analysis_results"]["comparison"]["savings"]["monthly"]
        analysis_msg = f"Scenario comparison completed. Monthly savings: ${savings:,.2f}"
        state["messages"].append(AIMessage(content=analysis_msg))
        
    except Exception as e:
        state["messages"].append(AIMessage(content=f"Error comparing scenarios: {e}"))
    
    return state

def generate_comparisons(state: MortgageState) -> MortgageState:
    """Generate personalized comparisons"""
    try:
        # Create LLM for comparisons

        api_token = os.getenv("ANTHROPIC_API_KEY")
        
        if not api_token:
            print("❌ ANTHROPIC_API_KEY not found in environment variables")
            state["messages"].append(AIMessage(content="Error: ANTHROPIC_API_KEY not configured"))
            return state
        
        
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20240620",
            temperature=0.1,
            max_tokens=1024,
            timeout=None,
            max_retries=2,
            anthropic_api_key=api_token,
        )
  
        print("✅ ChatAnthropic LLM initialized successfully for comparisons!")
        # print(f"🔍 State keys: {list(state.keys())}")
        
        try:
            context = {
                "current_loans": state["analysis_results"]["current_loans"],
            }

            print(f"✅ Context created successfully!")
        except KeyError as e:
            print(f"❌ Missing key in state: {e}")
            # Create a minimal context with available data
            context = {
                "current_loans": state.get("analysis_results", {}).get("current_loans", {}),
                "restructure_options": state.get("analysis_results", {}).get("restructure_options", {}),
                "comparison": state.get("analysis_results", {}).get("comparison", {}),
                "user_goals": state.get("user_goals", {})
            }
            print("✅ Created fallback context with available data")
        except Exception as e:
            print(f"❌ Error creating context: {e}")
            return state
        

        
        try:    
            prompt = f"""Based on the following mortgage analysis, provide personalized comparisons:

Current Situation:
- Total Balance: ${context['current_loans']['total_balance']:,.2f}
- Monthly Payment: ${context['current_loans']['total_monthly_payment']:,.2f}



User Goals: 

Please provide:
1. Break-even analysis considerations
2. Risk factors to consider
3. Final comparison with reasoning"""
            

        except Exception as e:
            print(f"❌ Error creating prompt: {e}. Creating a fallback prompt.")
            prompt = "Based on the mortgage analysis data, provide personalized comparisons and recommendations."
        
        
        try:
            response = llm.invoke(prompt)
            print("✅ ChatAnthropic LLM invoked successfully!")
            state["comparisons"] = {"analysis": response, "context": context}
            state["messages"].append(AIMessage(content="✅ Personalized comparisons generated successfully! Analysis complete with detailed recommendations."))
        except Exception as llm_error:
            error_msg = f"Error calling LLM for comparisons: {llm_error}"
            print(f"❌ {error_msg}")
            # Set a fallback response
            state["comparisons"] = {
                "analysis": "Unable to generate AI comparisons due to technical error. Please check your API configuration.",
                "context": context,
                "error": str(llm_error)
            }
            state["messages"].append(AIMessage(content=error_msg))
        
    except Exception as e:
        state["messages"].append(AIMessage(content=f"Error generating comparisons: {e}"))
    
    return state


# Create the workflow graph
def create_mortgage_workflow():
    """Create the Mortgage Comparisonworkflow"""
    
    # Create the graph
    workflow = StateGraph(MortgageState)
    
    # Add nodes
    workflow.add_node("analyze_current_loans", analyze_current_loans)
    workflow.add_node("analyze_restructure_options", analyze_restructure_options)
    workflow.add_node("compare_scenarios", compare_scenarios)
    workflow.add_node("generate_comparisons", generate_comparisons)
    
    # Add edges starting from START
    workflow.add_edge("analyze_current_loans", "analyze_restructure_options")
    workflow.add_edge("analyze_restructure_options", "compare_scenarios")
    workflow.add_edge("compare_scenarios", "generate_comparisons")
    workflow.add_edge("generate_comparisons", END)
    
    # Set the entry point
    workflow.set_entry_point("analyze_current_loans")
    
    return workflow.compile()

def run_mortgage_analysis(mortgage_data: dict, user_goals: dict = None) -> dict:
    """Run the complete mortgage analysis workflow"""
    
    if user_goals is None:
        user_goals = {
            "primary_goal": "monthly_savings",
            "risk_tolerance": "moderate",
            "time_horizon": "long_term",
            "additional_considerations": "Build equity faster"
        }
        print("No user goals provided. Using default goals.{user_goals}")
    
    # Initialize state
    initial_state = {
        "messages": [SystemMessage(content="You are a professional mortgage advisor. Analyze the provided mortgage data and provide comparisons.")],
        "current_loans": mortgage_data["existing_loans"],
        "restructure_options": mortgage_data["restructure_options"],
        "analysis_results": {},
        "comparisons": {},
        "user_goals": user_goals
    }
    
    # Create and run workflow
    workflow = create_mortgage_workflow()
    result = workflow.invoke(initial_state)
    # print("✅ Analysis Workflow completed successfully!")
    return result

def interactive_mortgage_agent():
    """Interactive mortgage agent using LangGraph"""
    
    print("🏠 Mortgage ComparisonAgent (LangGraph) initialized!")
    print("I can help you with comprehensive mortgage analysis and comparisons.")
    print("Type 'quit' to exit.")
    print("-" * 60)
    
    # Ask user which mortgage data file to use
    while True:
        print("\n📁 Available mortgage data files:")
        print("1. mortgage_data.json (default)")
        print("2. mortgage_data_private.json")
        
        file_choice = input("\nEnter your choice (1 or 2): ").strip()
        
        if file_choice == "1":
            filename = "mortgage_data.json"
            break
        elif file_choice == "2":
            filename = "mortgage_data_private.json"
            break
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")
    
    # Load selected data file
    try:
        with open(filename, 'r') as file:
            mortgage_data = json.load(file)
        print(f"✅ Successfully loaded {filename}")
    except FileNotFoundError:
        print(f"❌ {filename} not found. Please ensure the file exists.")
        return
    except json.JSONDecodeError:
        print(f"❌ Error reading {filename}. Please check the JSON format.")
        return
    
    # Show a summary of the loaded data
    print(f"\n📋 Loaded Data Summary:")
    print(f"   • {len(mortgage_data['existing_loans'])} existing loans")
    print(f"   • {len(mortgage_data['restructure_options'])} restructuring options")
    print(f"   • Total current balance: ${sum(loan['balance'] for loan in mortgage_data['existing_loans']):,.2f}")
    
    print(f"\n💬 Interactive Chat Session Started!")
    print(f"   Ask me questions about your mortgage restructuring options.")
    print(f"   Examples: 'I want to reduce monthly payments', 'Show me conservative options', 'What's the best rate?'")
    print(f"   Type 'quit' to exit.")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!!")
                break
                
            if not user_input:
                continue
            
            # Determine user goals from input
            user_goals = {
                "primary_goal": "monthly_savings" if "monthly" in user_input.lower() else "total_savings",
                "risk_tolerance": "low" if "conservative" in user_input.lower() else "moderate",
                "time_horizon": "short_term" if "short" in user_input.lower() else "long_term",
                "additional_considerations": user_input
            }
            
            print("🤖 Running comprehensive mortgage analysis...")
            
            # Run the workflow
            result = run_mortgage_analysis(mortgage_data, user_goals)
            
            # Display results
            print("\n📊 ANALYSIS RESULTS:")
            print("-" * 30)
            
            if "analysis_results" in result:
                current = result["analysis_results"].get("current_loans", {})
                if current:
                    print(f"Current Total Balance: ${current.get('total_balance', 0):,.2f}")
                    print(f"Current Monthly Payment: ${current.get('total_monthly_payment', 0):,.2f}")
                
                comparison = result["analysis_results"].get("comparison", {})
                if comparison:
                    savings = comparison.get("savings", {})
                    print(f"Monthly Savings: ${savings.get('monthly', 0):,.2f}")
            
            if "comparisons" in result and "analysis" in result["comparisons"]:
                print("\n💡 COMPARISONS:")
                print("-" * 20)
                print(result["comparisons"]["analysis"])
            
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Good luck with your mortgage restructuring!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again with a different question.")
            print("-" * 60)

def main():
    interactive_mortgage_agent()

if __name__ == "__main__":
    main() 