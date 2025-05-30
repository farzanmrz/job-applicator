# Imports
from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from phoenix.otel import register as phoenix_register
from smolagents import CodeAgent, LiteLLMModel
from smolagents.agents import PromptTemplates

# Constants
OLLAMA_MODEL_ID = "ollama_chat/qwen3:30b-a3b"  # Your specified model
OLLAMA_API_BASE = "http://localhost:11434"

# (Your existing imports and constants)
# ...


# 👇 MODULAR STREAMING FUNCTION
def stream_and_print_response(response_generator) -> str:
    """
    Iterates over a response generator, prints each chunk to the console,
    and returns the accumulated full response.

    Args:
        response_generator: The generator object yielding response chunks.

    Returns:
        str: The accumulated full response.
    """
    full_response = ""
    for chunk in response_generator:
        if isinstance(chunk, str):  # Assuming the streamed chunks are strings
            print(chunk, end="", flush=True)
            full_response += chunk

    return full_response


# Functions
def start_chat_session():
    """
    Initializes the agent and starts a conversational loop in the terminal.
    """
    # Setup TELEMETRY
    phoenix_register()
    SmolagentsInstrumentor().instrument()

    # Initialize model/agent
    llm_basic_chat = LiteLLMModel(
        model_id=OLLAMA_MODEL_ID,
        api_base=OLLAMA_API_BASE,
    )

    agent = CodeAgent(
        name="BasicChatAgent",
        description="The base level chat agent which the user interacts with and this is the primary orchestrator as well as the main entry and exit point of functionality.",
        model=llm_basic_chat,
        tools=[],
        managed_agents=[],
        add_base_tools=False,
        # prompt_templates=None,
        planning_interval=None,
        max_print_outputs_length=20,
        provide_run_summary=False,
        final_answer_checks=None,
        # Exclusive
        stream_outputs=True,
        additional_authorized_imports=[],
        verbosity_level=20,
        max_steps=20,
        executor_type="local",
        executor_kwargs=None,
        use_structured_outputs_internally=False,
    )
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
        # stream=False will make agent.run return the full response string
        agent_response = agent.run(
            task=user_input,
            stream=False,
            reset=False,
            images=None,
            additional_args=None,
            max_steps=agent.max_steps,
        )

        print(f"Agent: {agent_response}")


# Main script execution
if __name__ == "__main__":
    start_chat_session()
