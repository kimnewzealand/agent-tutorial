import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint
from langchain.schema import HumanMessage, SystemMessage, AIMessage

load_dotenv()

def is_vague_input(user_input):
    """Check if user input is vague and needs clarification"""
    vague_terms = [
        'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
        'help', 'assist', 'support', 'guide', 'advice', 'tips',
        'cook', 'make', 'prepare', 'recipe', 'food', 'dish',
        'something', 'anything', 'whatever', 'idk', "i don't know"
    ]
    
    user_lower = user_input.lower().strip()
    
    # Check if input is just a greeting or very general
    for term in vague_terms:
        if term in user_lower and len(user_input.split()) <= 3:
            return True
    
    # Check if input is too short or unclear
    if len(user_input.split()) < 2:
        return True
        
    return False

def get_clarification_prompt(user_input):
    """Generate a specific clarification question based on the vague input"""
    user_lower = user_input.lower().strip()
    
    if any(greeting in user_lower for greeting in ['hello', 'hi', 'hey']):
        return "Hello! I'm here to help with cooking. What specific dish or cooking technique would you like to learn about?"
    
    if 'help' in user_lower or 'assist' in user_lower:
        return "I'd be happy to help with cooking! What specific recipe or cooking question do you have?"
    
    if 'cook' in user_lower or 'make' in user_lower or 'recipe' in user_lower:
        return "Great! What specific dish would you like to cook? Please let me know the name of the dish or the main ingredient you want to work with."
    
    return "I'd like to help you with cooking! Could you please be more specific about what you'd like to learn or make?"

def chat_with_model():
    api_token = os.getenv("HF_API_KEY")
    if not api_token:
        print("HF_API_KEY not found in environment variables.")
        return

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
        return

    # Initialize conversation with a system message
    messages = [
        SystemMessage(content="You are a helpful cooking assistant. Provide clear, step-by-step instructions for recipes and cooking techniques when users ask specific questions. Respond only to the current question without referencing previous conversation context.")
    ]
    
    print("Chat initialized! Type 'quit' to exit.")
    print("-" * 50)
    
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
            
        if not user_input:
            continue
        
        # Check if input is vague and needs clarification
        if is_vague_input(user_input):
            clarification = get_clarification_prompt(user_input)
            print(f"Assistant: {clarification}")
            print("-" * 50)
            continue
            
        # Add user message to conversation
        messages.append(HumanMessage(content=user_input))
        
        try:
            # Create a conversation string from messages (excluding the current user input)
            conversation = ""
            for message in messages:
                if isinstance(message, SystemMessage):
                    conversation += f"System: {message.content}\n"
                elif isinstance(message, HumanMessage):
                    conversation += f"Human: {message.content}\n"
                elif isinstance(message, AIMessage):
                    conversation += f"Assistant: {message.content}\n"
            
            # Add the current user input to the conversation string
            conversation += f"Human: {user_input}\n"
            
            # Get response from model
            response = llm.invoke(conversation)
            
            # Add AI response to conversation
            ai_message = AIMessage(content=response)
            messages.append(ai_message)
            
            print(f"Assistant: {response}")
            print("-" * 50)
            
        except Exception as e:
            print(f"Error getting response: {e}")
            print("-" * 50)

def main():
    chat_with_model()

if __name__ == "__main__":
    main()
