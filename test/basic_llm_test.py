# Imports
from smolagents import CodeAgent, LiteLLMModel

# Constants
OLLAMA_MODEL_ID = "ollama_chat/gemma3:12b-it-qat"  # Your specified model
OLLAMA_API_BASE = "http://localhost:11434"


# Functions
def start_chat_session():
    """
    Initializes the agent and starts a conversational loop in the terminal.
    """
    # Initialize model/agent with verbosity 0 for clean output
    llm_model = LiteLLMModel(
        model_id=OLLAMA_MODEL_ID,
        api_base=OLLAMA_API_BASE,
    )
    agent = CodeAgent(model=llm_model, tools=[], verbosity_level=0)
    print(
        f"ChatAgent session with {OLLAMA_MODEL_ID} started. Type your message or 'q' to quit."
    )

    # Start the chat loop only quitting with 'q'
    while True:
        user_input = input("\nYou: ")

        if user_input.lower() == "q":
            print("Agent: Goodbye!")
            break

        # Use reset=False to maintain the conversation history in the agent's memory
        agent_response = agent.run(user_input, reset=False)

        print(f"Agent: {agent_response}")


# Main script execution
if __name__ == "__main__":
    start_chat_session()
