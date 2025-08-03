HuggingFaceEndpoint initialized successfully.
C:\Users\ddobs\Documents\agent-tutorial\how_to_make_curry.py:80: LangChainDeprecationWarning: LangChain agents will continue to be supported, but it is recommended for new use cases to be built with LangGraph. LangGraph offers a more flexible and full-featured framework for building agents, including support for tool-calling, persistence of state, and human-in-the-loop workflows. For details, refer to the `LangGraph documentation <https://langchain-ai.github.io/langgraph/>`_ as well as guides for `Migrating from AgentExecutor <https://python.langchain.com/docs/how_to/migrate_agent/>`_ and LangGraph's `Pre-built ReAct agent <https://langchain-ai.github.io/langgraph/how-tos/create-react-agent/>`_.
  agent = initialize_agent(
🍳 Curry Cooking Agent initialized!
I can help you with:
- Finding curry recipes
- Checking ingredients
- Explaining cooking steps
- Providing cooking tips
Type 'quit' to exit.
------------------------------------------------------------
You: how do I make malaysian cuury
🤖 Agent is thinking...
C:\Users\ddobs\Documents\agent-tutorial\how_to_make_curry.py:121: LangChainDeprecationWarning: The method `Chain.run` was deprecated in langchain 0.1.0 and will be removed in 1.0. Use :meth:`~invoke` instead.
  response = agent.run(user_input)


> Entering new AgentExecutor chain...
 I should search for a recipe for malaysian cuisine
Action: recipe_search
Action Input: malaysian cuisine
Observation: Recipe search results for: malaysian cuisine
Thought: I should check if the ingredients are available
Action: ingredient_check
Action Input: malaysian cuisine
Observation: Ingredient check for: malaysian cuisine
Thought: I should provide detailed instructions for a specific cooking step
Action: cooking_step
Action Input: malaysian cuisine
Observation: Detailed instructions for: malaysian cuisine
Thought: I now know the final answer
Final Answer: The final answer to the original input question

> Finished chain.
Assistant: The final answer to the original input question
------------------------------------------------------------
You: quit
👋 Goodbye! Happy cooking!