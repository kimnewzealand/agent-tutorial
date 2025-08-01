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


## Overview of tools

### Hugging Face 

> [The Hugging Face Model Hub is a repository where you can find pre-trained models for a wide range of tasks, such as natural language processing (NLP), computer vision, audio processing, and more.](https://huggingface.co/models)

The API Key is free so this is a convenient source of models to learn on.

### LangChain

> [LangChain is a framework for developing applications powered by large language models (LLMs).](https://python.langchain.com/docs/introduction/)

LangChain is useful for building AI agents that can interact with language models, manage complex workflows, and integrate external data sources. It simplifies tasks such as prompt engineering, chaining multiple LLM calls, and connecting to APIs or databases, making it easier to create robust, production-ready AI applications. 

LangChain is open source, allowing developers to freely use, modify, and contribute to the framework.




## Setup

Follow these steps to set up your environment:

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
