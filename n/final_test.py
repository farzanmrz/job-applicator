import asyncio
from datetime import datetime
from enum import Enum
from typing import List, Optional

# --- Autogen Imports ---
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.ui import Console
from autogen_core.models import UserMessage
from autogen_ext.models.ollama import OllamaChatCompletionClient as set_model

# --- Pydantic Imports ---
from pydantic import BaseModel

# Prompts Common MD
from common.constants import llama32fp16_3b, qwen3_30b, qwen3_1_7b, llama32_1b
from prompts.out_ext import OutExtEdu, OutExtExp

# Prompts specific
from prompts.sysmsg_ext import sysmsgExtLkdEdu, sysmsgExtResEdu, sysmsgCombEdu, sysmsgExtResExp, sysmsgExtLkdExp, sysmsgCombExp

# Clients setup
llm_qwen3_30b = set_model(**qwen3_30b)
llm_llama32fp16_3b = set_model(**llama32fp16_3b)
llm_qwen3_1_7b = set_model(**qwen3_1_7b)
llm_qwen3_1_7b_1 = set_model(**qwen3_1_7b)
llm_llama32_1b = set_model(**llama32_1b)
llm_llama32_1b_1 = set_model(**llama32_1b)
llm_llama32_1b_2 = set_model(**llama32_1b)

# Main
async def main():

    # Define your agents
    agt_ext_in_edu = AssistantAgent(
        name="ExtInEdu",
        system_message="You have one job. No matter what the user says, you will ALWAYS respond with the following exact phrase and nothing else: 'Please extract the education details from the markdown file'",
        model_client=llm_llama32_1b_1,
        # model_client_stream=True,
    )


    agt_ext_res_edu = AssistantAgent(
        name="ExtResEdu",
        system_message=sysmsgExtResEdu,
        model_client=llm_qwen3_1_7b,
        # model_client_stream=True,
        output_content_type=OutExtEdu,
    )

    agt_ext_lkd_edu = AssistantAgent(
        name="ExtLkdEdu",
        system_message=sysmsgExtLkdEdu,
        model_client=llm_qwen3_1_7b,
        # model_client_stream=True,
        output_content_type=OutExtEdu,
    )

    agt_comb_edu = AssistantAgent(
        name="CombEdu",
        system_message=sysmsgCombEdu,
        model_client=llm_qwen3_1_7b,
        # model_client_stream=True,
        output_content_type=OutExtEdu, 
    )

    # Setup graph
    builder = DiGraphBuilder()
    builder.add_node(agt_ext_in_edu).add_node(agt_ext_res_edu).add_node(agt_ext_lkd_edu).add_node(agt_comb_edu)

    # Add parallel edges
    builder.add_edge(agt_ext_in_edu, agt_ext_res_edu)
    builder.add_edge(agt_ext_in_edu, agt_ext_lkd_edu)

    # Add combination agent
    builder.add_edge(agt_ext_res_edu, agt_comb_edu)
    builder.add_edge(agt_ext_lkd_edu, agt_comb_edu)
    flow = GraphFlow(participants=builder.get_participants(), graph=builder.build())

    # Define initial prompts
    initial_task = f"Start the flow"
    await Console(flow.run_stream(task=initial_task), output_stats=True)

    # --- Cleanup ---
    await llm_qwen3_30b.close()
    await llm_llama32fp16_3b.close()
    await llm_qwen3_1_7b.close()
    await llm_llama32_1b.close()


if __name__ == "__main__":
    asyncio.run(main())
