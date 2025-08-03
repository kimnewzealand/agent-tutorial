import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.tools import BaseTool
from typing import Optional
from pydantic import BaseModel, Field

load_dotenv()

class RecipeSearchInput(BaseModel):
    query: str = Field(description="The cooking query or recipe request")

class RecipeSearchTool(BaseTool):
    name: str = "recipe_search"
    description: str = "Search for recipes and cooking instructions"
    args_schema: type[BaseModel] = RecipeSearchInput
    
    def _run(self, query: str) -> str:
        """Search for recipes and cooking instructions"""
        
        if "curry" in query.lower():
            return f"Based on your query '{query}', I can help you find curry recipes. In a full implementation, this tool would search multiple recipe sources and return the best matches. For now, I can provide general curry cooking guidance and techniques."
        
        return f"I can help you find recipes for '{query}'. This tool is designed to search across multiple recipe sources and provide you with the best cooking instructions available."

class IngredientCheckInput(BaseModel):
    ingredients: str = Field(description="List of ingredients to check")

class IngredientCheckTool(BaseTool):
    name: str = "ingredient_check"
    description: str = "Check if ingredients are available and suggest alternatives"
    args_schema: type[BaseModel] = IngredientCheckInput
    
    def _run(self, ingredients: str) -> str:
        """Check ingredient availability and suggest alternatives"""
        # This tool would typically:
        # - Connect to grocery store APIs to check availability
        # - Access ingredient substitution databases
        # - Use nutritional databases for alternatives
        # - Check local store inventories
        
        # For now, we'll provide general guidance
        return f"I can help you check ingredient availability for '{ingredients}'. In a full implementation, this tool would connect to grocery databases and provide real-time availability and substitution options."

class CookingStepInput(BaseModel):
    step: str = Field(description="The cooking step to explain")

class CookingStepTool(BaseTool):
    name: str = "cooking_step"
    description: str = "Provide detailed instructions for a specific cooking step"
    args_schema: type[BaseModel] = CookingStepInput
    
    def _run(self, step: str) -> str:
        """Provide detailed cooking step instructions"""
        # This tool would typically:
        # - Access cooking technique databases
        # - Connect to culinary education platforms
        # - Use video tutorial APIs
        # - Access professional chef knowledge bases
        
        # For now, we'll provide general guidance
        return f"I can help you understand the cooking step '{step}'. In a full implementation, this tool would access comprehensive cooking technique databases and provide detailed, professional instructions with tips and best practices."

def create_cooking_agent():
    """Create a cooking agent with HuggingFace model and tools"""
    
    # Initialize HuggingFace model
    api_token = os.getenv("HF_API_KEY")
    if not api_token:
        print("HF_API_KEY not found in environment variables.")
        return None

    try:
        llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-Nemo-Base-2407",
            provider="auto",
            max_new_tokens=1000,
            do_sample=False,
            huggingfacehub_api_token=api_token
        )
        print("HuggingFaceEndpoint initialized successfully.")
    except Exception as e:
        print(f"Error initializing HuggingFaceEndpoint: {e}")
        return None

    # Create tools
    tools = [
        RecipeSearchTool(),
        IngredientCheckTool(),
        CookingStepTool()
    ]

    # Create agent
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )

    return agent

def chat_with_cooking_agent():
    """Interactive chat with the cooking agent"""
    
    agent = create_cooking_agent()
    if not agent:
        return

    print("🍳 Curry Cooking Agent initialized!")
    print("I can help you with:")
    print("- Finding curry recipes")
    print("- Checking ingredients")
    print("- Explaining cooking steps")
    print("- Providing cooking tips")
    print("Type 'quit' to exit.")
    print("-" * 60)

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye! Happy cooking!")
                break
                
            if not user_input:
                continue

            # Process with agent
            print("🤖 Agent is thinking...")
            response = agent.run(user_input)
            print(f"Assistant: {response}")
            print("-" * 60)

        except KeyboardInterrupt:
            print("\n👋 Goodbye! Happy cooking!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again with a different question.")
            print("-" * 60)

def main():
    """Main function to run the cooking agent"""
    chat_with_cooking_agent()

if __name__ == "__main__":
    main() 