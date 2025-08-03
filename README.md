
# Python AI Agent From Scratch

This project follows the [Python AI Agent From Scratch](https://github.com/techwithtim/PythonAIAgentFromScratch) tutorial by Tech With Tim. It demonstrates how to build a simple AI agent using Python, focusing on core concepts such as environment interaction, agent design, and reinforcement learning basics.



## Tooling used in this project

### LangChain

> [LangChain is a framework for developing applications powered by large language models (LLMs).](https://python.langchain.com/docs/introduction/)

It simplifies and abstracts tasks such as prompt engineering, chaining multiple LLM calls, and connecting to APIs or databases

LangChain is also open source and free to use.

### Hugging Face 

> [The Hugging Face Model Hub is a repository where you can find pre-trained models for a wide range of tasks, such as natural language processing (NLP), computer vision, audio processing, and more.](https://huggingface.co/models)

The API Key include a free credits quota so this is a convenient source of models to learn on.



## Project Overview

I have made some variations from the tutorial's code:

I split the main.py into smaller examples scripts to see how the agent components work.

1.  First simple llm example. 
No agent functionality yet.

**SCRIPT** 
`how_to_make_bread.py`

**MODEL** 
Randomly picked model in HuggingFace. According to [Mistral-Nemo-Base-2407 model card ](https://huggingface.co/mistralai/Mistral-Nemo-Base-2407)
> The Mistral-Nemo-Base-2407 Large Language Model (LLM) is a pretrained generative text model of 12B parameters trained jointly by Mistral AI and NVIDIA

I used a langchain huggingface endpoint to access the model.

**PROMPT** 
I used a one line text coded prompt.

**OUTPUT** 
The output is printed in the console. See example outputs: `how_to_make_bread.md`


2.  Next, a simple llm chat example. 

The langchain_huggingface library doesn't have a direct equivalent to ChatOpenAI like ChatHuggingFace. This script uses the existing HuggingFaceEndpoint and LangChain's chat message system.

**SCRIPT** 
`how_to_make_cake.py`

**MODEL** 
Same model and endpoint [Mistral-Nemo-Base-2407 model card ](https://huggingface.co/mistralai/Mistral-Nemo-Base-2407)


**PROMPT** 
User Input: The script prompts you with input("You: ") and waits for you to type something
Message Creation: When you type something, the script creates a HumanMessage object to represent your input in the conversation context
Context Building: This message gets added to the messages list along with previous messages
Model Processing: The entire conversation (including your input) gets sent to the HuggingFace model

**OUTPUT** 
The conversational output is printed in the console. See example outputs: `how_to_make_cake.md`


3.  Next, a simple agent example. 

`how_to_make_curry.py` script that implements a proper LangChain agent with HuggingFace. 

**SCRIPT** 
`how_to_make_curry.py`

**MODEL** 
Same model and endpoint [Mistral-Nemo-Base-2407 model card ](https://huggingface.co/mistralai/Mistral-Nemo-Base-2407)


**PROMPT**

LangChain Agent: Uses ZERO_SHOT_REACT_DESCRIPTION agent type. It is a general task agent that doesn't need training.
Structured Input/Output: Uses Pydantic library models with logic to perform data validation and structure of the data. BaseModel = "What data do I expect?"
Interactive Chat: Clean console interface with emojis and formatting
Custom executable tools with function definition using Langchain library tools. BaseTool = "What do I do with that data?"
Agent Reasoning: The agent can decide which tools to use based on your query



**OUTPUT** 
The conversational output is printed in the console. See example outputs: `how_to_make_curry.md`

Verbose Mode: Shows the agent's thinking process

## Setup

Follow these steps to set up the environment:

1. **Create a virtual environment**:
    ```bash
    python -m venv .venv
    ```

    

2. **Activate the virtual environment**:
    - On Windows:
      ```bash
      .venv\Scripts\Activate
      ```
    - On macOS/Linux:
      ```bash
      source .venv/bin/activate
      ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt    
    ```
# Other References


[Andrej Karpathy: Software Is Changing (Again)](https://www.youtube.com/watch?v=LCEmiRjPEtQ)
- We’ve entered the era of “Software 3.0,” where natural language becomes the new programming interface and models do the rest.

## License

This project is for educational purposes and follows the license of the original tutorial repository.
