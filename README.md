# Python AI Agent From Scratch

This project follows the [Python AI Agent From Scratch](https://github.com/techwithtim/PythonAIAgentFromScratch) tutorial by Tech With Tim. It demonstrates how to build a simple AI agent using Python, focusing on core concepts such as environment interaction, agent design, and reinforcement learning basics.



## Overview of the agent lifecycle

The agent lifecycle typically consists of the following steps:

1. **Initialization**: The agent is created and its parameters are set.
2. **Observation**: The agent observes the current state of the environment.
3. **Decision Making**: Based on its observations, the agent selects an action using its policy or strategy.
4. **Action**: The agent performs the chosen action in the environment.
5. **Feedback**: The environment responds to the agent's action, providing new state information and a reward signal.
6. **Learning**: The agent updates its knowledge or policy based on the feedback received.
7. **Iteration**: Steps 2–6 are repeated until a stopping condition is met (e.g., a goal is reached or a maximum number of steps).

This cycle allows the agent to improve its performance over time through continuous interaction and learning.


## Tooling used in this project

### LangChain

> [LangChain is a framework for developing applications powered by large language models (LLMs).](https://python.langchain.com/docs/introduction/)

It simplifies and abstracts tasks such as prompt engineering, chaining multiple LLM calls, and connecting to APIs or databases

LangChain is also open source and free to use.

### Hugging Face 

> [The Hugging Face Model Hub is a repository where you can find pre-trained models for a wide range of tasks, such as natural language processing (NLP), computer vision, audio processing, and more.](https://huggingface.co/models)

The API Key is free so this is a convenient source of models to learn on.



## Project Overview

I have made some variations from the tutorial's code:

I split the main.py into smaller examples scripts to see how the agent components work.

1.  First simple agent example. This falls under the initialisation step in the lifecycle.

SCRIPT 
`how_to_make_bread.py`

MODEL 
Randomly picked model in HuggingFace. According to [Mistral-Nemo-Base-2407 model card ](https://huggingface.co/mistralai/Mistral-Nemo-Base-2407)
> The Mistral-Nemo-Base-2407 Large Language Model (LLM) is a pretrained generative text model of 12B parameters trained jointly by Mistral AI and NVIDIA

I used a langchain huggingface endpoint to access the model.

PROMPT 
I used a one line text coded prompt.

OUTPUT 
The output is printed in the console. See example outputs: `how_to_make_bread.md`

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


## License

This project is for educational purposes and follows the license of the original tutorial repository.
