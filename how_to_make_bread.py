import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint

load_dotenv()

def main():
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

    prompt = "What is the best method for making bread?"
    try:
        response = llm.invoke([prompt])
        print("Response:", response)
    except Exception as e:
        print(f"Error invoking llm: {e}")

if __name__ == "__main__":
    main()
