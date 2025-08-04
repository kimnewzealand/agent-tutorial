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

def generate_comparisons(state: MortgageState) -> MortgageState:
    """Generate comparisons"""
    if current_loans := state.get("analysis_results", {}).get("current_loans"):
        total_balance = current_loans['total_balance']
        total_monthly_payment = current_loans['total_monthly_payment']
    else:
        print("❌ No current loans found")
        return state

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
            max_tokens=1000,
            timeout=None,
            max_retries=2,
            anthropic_api_key=api_token,
        )
  
        print("✅ ChatAnthropic LLM initialized successfully for comparisons!")
        # print(f"🔍 State keys: {list(state.keys())}")
        
        try:
            context = {
                "current_loans": state["current_loans"],
                "market_conditions": state["market_conditions"],
                "user_goals": state["user_goals"]
            }

            print(f"✅ Context created successfully!")
        except KeyError as e:
            print(f"❌ Context error. Missing key in state: {e}")
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
            current_rates = context['market_conditions']['current_rates']
            floating_rate = current_rates['floating']
            six_month_rate = current_rates['6_months_fixed']
            twelve_month_rate = current_rates['12_months_fixed']
            eighteen_month_rate = current_rates['18_months_fixed']
            twenty_four_month_rate = current_rates['24_months_fixed']
            thirty_six_month_rate = current_rates['36_months_fixed']
            forty_eight_month_rate = current_rates['48_months_fixed']
            sixty_month_rate = current_rates['60_months_fixed']
            flexi_rate = current_rates['flexi']
            offset_rate = current_rates['offset']
            
            user_goals = context['user_goals']
            prompt = f"""Based on the following mortgage analysis, provide comparisons of combinations of two different rates and terms:

Current Situation:
- Total Balance: ${total_balance:,.2f}
- Monthly Payment: ${total_monthly_payment:,.2f}

Market Conditions:
- Current Rates: {floating_rate}%
- 6-Month Fixed Rates: {six_month_rate}%
- 12-Month Fixed Rates: {twelve_month_rate}%
- 18-Month Fixed Rates: {eighteen_month_rate}%
- 24-Month Fixed Rates: {twenty_four_month_rate}%
- 36-Month Fixed Rates: {thirty_six_month_rate}%
- 48-Month Fixed Rates: {forty_eight_month_rate}%
- 60-Month Fixed Rates: {sixty_month_rate}%
- Flexi Rate: {flexi_rate}%
- Offset Rate: {offset_rate}%

Considering the following user goals: {user_goals['primary_goal']}

Please provide:
1. Break-even analysis considerations
2. Risk factors to consider
3. Final comparison with reasoning"""
            
            print(f"✅ Prompt created !")
            print(f"{prompt}")
        except Exception as e:
            print(f"❌ Error creating prompt: {e}. Creating a fallback prompt.")
            prompt = "Based on the mortgage analysis data, provide personalized comparisons and recommendations."
        
        try:
            response = llm.invoke(prompt)
            print(f"✅ ChatAnthropic LLM invoked successfully!")
            state["comparisons"] = {"analysis": response, "context": context}
            success_msg = "✅ Personalized comparisons generated successfully! Analysis complete with detailed recommendations."
            print(f"{success_msg}")
            state["messages"].append(AIMessage(content=success_msg))
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


def interactive_mortgage_agent():
    """Interactive mortgage agent using LangGraph"""
    print(f"✅ Interactive mortgage agent started!")


def main():
    interactive_mortgage_agent()

if __name__ == "__main__":
    main() 