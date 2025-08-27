import os
import json
import time
from typing import Dict, Any
from dotenv import load_dotenv
from smolagents import CodeAgent, tool
from smolagents.models import LiteLLMModel

load_dotenv()

# Smolagents tool definitions
@tool
def analyze_loan_data(loan_data: str) -> str:
    """
    Analyze existing mortgage loans and calculate current payment obligations.

    Args:
        loan_data: JSON string containing existing loan information

    Returns:
        JSON string with analysis results including total balance, monthly payment, and weighted average rate
    """
    try:
        loans = json.loads(loan_data)
        existing_loans = loans.get('existing_loans', [])

        if not existing_loans:
            return json.dumps({"error": "No existing loans found in data"})

        total_balance = sum(loan.get('balance', 0) for loan in existing_loans)
        total_monthly_payment = sum(loan.get('monthly_payment', 0) for loan in existing_loans)

        if total_balance > 0:
            weighted_rate = sum(loan.get('balance', 0) * loan.get('rate', 0) for loan in existing_loans) / total_balance
        else:
            weighted_rate = 0

        analysis = {
            "total_balance": total_balance,
            "total_monthly_payment": total_monthly_payment,
            "weighted_average_rate": weighted_rate,
            "loan_count": len(existing_loans),
            "loans": existing_loans
        }

        return json.dumps(analysis)
    except Exception as e:
        return json.dumps({"error": f"Error analyzing loan data: {e}"})

@tool
def calculate_restructure_options(current_analysis: str, market_rates: str, user_goals: str) -> str:
    """
    Calculate potential restructuring options by dividing the total loan into 2 equal loans
    and comparing combinations of different rates for each loan.

    Args:
        current_analysis: JSON string with current loan analysis
        market_rates: JSON string with current market rates
        user_goals: JSON string with user's financial goals and preferences

    Returns:
        JSON string with restructuring options showing combinations of 2 loans with different rates
    """
    try:
        analysis = json.loads(current_analysis)
        rates = json.loads(market_rates)
        goals = json.loads(user_goals)

        current_balance = analysis.get('total_balance', 0)
        # Try multiple possible keys for current payment
        current_payment = (analysis.get('total_monthly_payment', 0) or
                          analysis.get('total_monthly_payments', 0) or
                          analysis.get('current_monthly_payment', 0))



        # Divide into 2 equal loans
        loan_amount = current_balance / 2

        # Available rate types (matching the actual keys in market data)
        rate_types = ['floating', 'flexi', 'offset', '6_months_fixed', '12_months_fixed',
                     '18_months_fixed', '24_months_fixed', '36_months_fixed', '48_months_fixed', '60_months_fixed']

        # Get available rates - handle both formats
        available_rates = {}

        # Check if rates are nested under 'current_rates' or at the top level
        if 'current_rates' in rates:
            current_rates = rates['current_rates']
        else:
            current_rates = rates

        for rate_type in rate_types:
            if rate_type in current_rates:
                available_rates[rate_type] = current_rates[rate_type]



        # Generate combinations of 2 loans with different rate combinations
        combinations = []



        for rate1_type, rate1_value in available_rates.items():
            for rate2_type, rate2_value in available_rates.items():
                # Calculate monthly payments for each loan (assuming 25-year term)
                monthly_rate1 = rate1_value / 100 / 12
                monthly_rate2 = rate2_value / 100 / 12
                term_months = 25 * 12  # 25 years

                # Monthly payment calculation: P * [r(1+r)^n] / [(1+r)^n - 1]
                if monthly_rate1 > 0:
                    payment1 = loan_amount * (monthly_rate1 * (1 + monthly_rate1)**term_months) / ((1 + monthly_rate1)**term_months - 1)
                else:
                    payment1 = loan_amount / term_months

                if monthly_rate2 > 0:
                    payment2 = loan_amount * (monthly_rate2 * (1 + monthly_rate2)**term_months) / ((1 + monthly_rate2)**term_months - 1)
                else:
                    payment2 = loan_amount / term_months

                total_new_payment = payment1 + payment2
                monthly_savings = current_payment - total_new_payment
                annual_savings = monthly_savings * 12

                # Calculate weighted average rate
                weighted_avg_rate = (rate1_value + rate2_value) / 2

                combination = {
                    "loan1": {
                        "amount": loan_amount,
                        "rate_type": rate1_type,
                        "rate": rate1_value,
                        "monthly_payment": payment1
                    },
                    "loan2": {
                        "amount": loan_amount,
                        "rate_type": rate2_type,
                        "rate": rate2_value,
                        "monthly_payment": payment2
                    },
                    "total_monthly_payment": total_new_payment,
                    "monthly_savings": monthly_savings,
                    "annual_savings": annual_savings,
                    "weighted_average_rate": weighted_avg_rate,
                    "combination_name": f"{rate1_type} + {rate2_type}"
                }

                combinations.append(combination)



        # Sort by monthly savings (descending) and remove duplicates
        combinations.sort(key=lambda x: x['monthly_savings'], reverse=True)

        # Remove duplicate combinations (same rates in different order)
        unique_combinations = []
        seen_combinations = set()

        for combo in combinations:
            # Create a sorted tuple of rate types to identify duplicates
            rate_pair = tuple(sorted([combo['loan1']['rate_type'], combo['loan2']['rate_type']]))
            if rate_pair not in seen_combinations:
                seen_combinations.add(rate_pair)
                unique_combinations.append(combo)



        result = {
            "current_situation": {
                "total_balance": current_balance,
                "current_monthly_payment": current_payment
            },
            "restructure_strategy": "Split into 2 equal loans with different rate combinations",
            "loan_structure": {
                "loan1_amount": loan_amount,
                "loan2_amount": loan_amount,
                "total_amount": current_balance
            },
            "top_combinations": unique_combinations[:15],  # Top 15 unique combinations
            "user_goals": goals
        }

        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": f"Error calculating restructure options: {e}"})

# Mortgage Agent Class using smolagents
class MortgageAgent:
    """Mortgage restructuring agent using smolagents framework with rate limiting"""

    def __init__(self):
        """Initialize the mortgage agent with Anthropic model and rate limiting"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        # Initialize the Anthropic model using LiteLLM
        self.model = LiteLLMModel(
            model_id="claude-3-5-sonnet-20240620",
            api_key=api_key
        )

        # Initialize the agent with tools and additional imports
        self.agent = CodeAgent(
            tools=[analyze_loan_data, calculate_restructure_options],
            model=self.model,
            max_steps=8,  # Reduced to limit token usage
            additional_authorized_imports=["json"]
        )

        # Rate limiting variables
        self.last_request_time = 0
        self.min_request_interval = 2.0  # Minimum 2 seconds between requests

        print("✅ Mortgage Agent initialized with smolagents and rate limiting!")

    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits by waiting between requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last_request
            print(f"⏳ Rate limiting: waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)

        self.last_request_time = time.time()

    def _run_agent_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Run agent with retry logic for rate limit errors"""
        for attempt in range(max_retries):
            try:
                self._wait_for_rate_limit()
                result = self.agent.run(prompt)

                # Extract content from result
                if hasattr(result, 'content'):
                    return result.content
                else:
                    return str(result)

            except Exception as e:
                error_str = str(e).lower()
                if "rate_limit" in error_str or "rate limit" in error_str:
                    wait_time = (attempt + 1) * 5  # Exponential backoff: 5, 10, 15 seconds
                    print(f"⚠️  Rate limit hit (attempt {attempt + 1}/{max_retries}). Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    if attempt == max_retries - 1:
                        return f"Rate limit exceeded after {max_retries} attempts. Please try again later."
                else:
                    print(f"❌ Error in agent execution: {e}")
                    return f"Error: {e}"

        return "Maximum retries exceeded"

    def analyze_current_loans(self, mortgage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current mortgage loans using the agent"""
        try:
            loan_data_json = json.dumps(mortgage_data)

            # Create a structured task decomposition prompt for the agent to analyze the loan data
            prompt = f"""
            Analyze the mortgage loan data using the analyze_loan_data tool:

            {loan_data_json}

            Provide insights about:
            1. Total balance across all loans
            2. Total monthly payments
            3. Weighted average interest rate
            4. Number of loans
            5. Effective remaining term

            Return structured results.
            """

            content = self._run_agent_with_retry(prompt)

            # Try to extract JSON from the result
            try:
                # Look for JSON in the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    agent_data = json.loads(json_match.group())
                    # Convert agent format to expected format
                    def extract_numeric_value(value):
                        """Extract numeric value from formatted strings like '$40,000' or '4.5%'"""
                        if isinstance(value, (int, float)):
                            return value
                        if isinstance(value, str):
                            # Remove currency symbols, commas, and percentage signs
                            cleaned = value.replace('$', '').replace(',', '').replace('%', '')
                            try:
                                return float(cleaned)
                            except ValueError:
                                return 0
                        return 0

                    if "Total balance across all loans" in agent_data:
                        analysis_data = {
                            "total_balance": extract_numeric_value(agent_data.get("Total balance across all loans", 0)),
                            "total_monthly_payment": extract_numeric_value(agent_data.get("Total monthly payments", 0)),
                            "weighted_average_rate": extract_numeric_value(agent_data.get("Weighted average interest rate", 0)),
                            "loan_count": extract_numeric_value(agent_data.get("Number of loans", 0))
                        }
                    elif "total_balance" in agent_data:
                        # Already in correct format
                        analysis_data = agent_data
                    else:
                        analysis_data = agent_data
                else:
                    # Fallback: use the tool directly
                    analysis_data = json.loads(analyze_loan_data(loan_data_json))
            except:
                # Final fallback: use the tool directly
                analysis_data = json.loads(analyze_loan_data(loan_data_json))

            return {
                "analysis_results": {"current_loans": analysis_data},
                "agent_response": content
            }

        except Exception as e:
            print(f"❌ Error in analyze_current_loans: {e}")
            return {
                "analysis_results": {"current_loans": {"error": str(e)}},
                "agent_response": f"Error analyzing loans: {e}"
            }

    def generate_comparisons(self, mortgage_data: Dict[str, Any], user_goals: Dict[str, Any], analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized mortgage comparisons using the agent"""
        try:
            current_loans = analysis_results.get("current_loans", {})
            if not current_loans or "error" in current_loans:
                print("❌ No valid current loans analysis found")
                return {"error": "No valid loan analysis available"}

            # Prepare data for the agent
            market_conditions = mortgage_data.get("market_conditions", {})

            # Create a tool directed prompt for the agent to generate comparisons
            prompt = f"""
            Analyze mortgage restructuring options for this client:

            Current Analysis: {json.dumps(current_loans)}
            Market Rates: {json.dumps(market_conditions.get('current_rates', {}))}
            User Goal: {user_goals.get('primary_goal', 'savings')}

            Use calculate_restructure_options tool to analyze 2-loan combinations.

            Provide:
            1. Current Situation Summary
            2. Top 3 Loan Combinations
            3. Monthly Savings for each
            4. Rate Strategy Analysis
            5. Final Recommendation

            Be concise and specific.
            """

            # Use the agent with retry logic
            analysis_content = self._run_agent_with_retry(prompt)

            print("✅ Personalized comparisons generated successfully!")

            return {
                "analysis": analysis_content,
                "context": {
                    "current_loans": current_loans,
                    "market_conditions": market_conditions,
                    "user_goals": user_goals
                }
            }

        except Exception as e:
            print(f"❌ Error generating comparisons: {e}")
            return {
                "error": f"Error generating comparisons: {e}",
                "analysis": "Unable to generate personalized comparisons due to technical error."
            }



# Global agent instance
_agent_instance = None

def get_agent() -> MortgageAgent:
    """Get or create the global agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = MortgageAgent()
    return _agent_instance

# Convenience functions for backward compatibility with the web demo
def analyze_current_loans(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Backward compatibility function for the web demo.
    Converts old state format to new agent format.
    """
    try:
        agent = get_agent()

        # Extract mortgage data from state
        mortgage_data = {
            "existing_loans": state.get("current_loans", []),
            "market_conditions": state.get("market_conditions", {})
        }

        # Analyze loans using the agent
        result = agent.analyze_current_loans(mortgage_data)

        # Update state with results
        state["analysis_results"] = result.get("analysis_results", {})

        return state

    except Exception as e:
        print(f"❌ Error in analyze_current_loans wrapper: {e}")
        state["analysis_results"] = {"current_loans": {"error": str(e)}}
        return state

def generate_comparisons(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Backward compatibility function for the web demo.
    Converts old state format to new agent format.
    """
    try:
        agent = get_agent()

        # Extract data from state
        mortgage_data = {
            "existing_loans": state.get("current_loans", []),
            "market_conditions": state.get("market_conditions", {}),
            "restructure_options": state.get("restructure_options", [])
        }
        user_goals = state.get("user_goals", {})
        analysis_results = state.get("analysis_results", {})

        # Generate comparisons using the agent
        result = agent.generate_comparisons(mortgage_data, user_goals, analysis_results)

        # Update state with results
        state["comparisons"] = result

        return state

    except Exception as e:
        print(f"❌ Error in generate_comparisons wrapper: {e}")
        state["comparisons"] = {"error": str(e), "analysis": f"Error generating comparisons: {e}"}
        return state

def interactive_mortgage_agent():
    """Interactive mortgage agent using smolagents"""
    try:
        get_agent()
        print("🏠 Welcome to the Mortgage Restructuring Agent!")
        print("✅ Agent initialized successfully!")

        # Example usage
        print("\n📋 Example: To use this agent in your application:")
        print("1. Call analyze_current_loans() with your mortgage data")
        print("2. Call generate_comparisons() with user goals and market conditions")
        print("3. The agent will provide personalized recommendations")

    except Exception as e:
        print(f"❌ Error initializing interactive agent: {e}")

def main():
    interactive_mortgage_agent()

if __name__ == "__main__":
    main()