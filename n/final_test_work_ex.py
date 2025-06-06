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
from common.constants import llama32_1b, llama32fp16_3b, qwen3_1_7b, qwen3_30b
from prompts.out_ext import OutExtEdu, OutExtExp

# Prompts specific
from prompts.sysmsg_ext import (
    sysmsgCombEdu,
    sysmsgCombExp,
    sysmsgExtLkdEdu,
    sysmsgExtLkdExp,
    sysmsgExtResEdu,
    sysmsgExtResExp,
)

# Clients setup
llm_qwen3_30b = set_model(**qwen3_30b)
llm_llama32fp16_3b = set_model(**llama32fp16_3b)
llm_qwen3_1_7b = set_model(**qwen3_1_7b)
llm_llama32_1b = set_model(**llama32_1b)


# Main
async def main():

    agt_ext_in_exp = AssistantAgent(
        name="ExtInExp",
        system_message="You have one job. No matter what the user says, you will ALWAYS respond with the following exact phrase and nothing else: 'Please extract the work experience details from the markdown file'",
        model_client=llm_llama32_1b,
        # model_client_stream=True,
    )

    agt_ext_res_exp = AssistantAgent(
        name="ExtResExp",
        system_message=sysmsgExtResExp,
        model_client=llm_qwen3_30b,
        # model_client_stream=True,
        output_content_type=OutExtExp,
    )

    agt_ext_lkd_exp = AssistantAgent(
        name="ExtLkdExp",
        system_message=sysmsgExtLkdExp,
        model_client=llm_qwen3_30b,
        # model_client_stream=True,
        output_content_type=OutExtExp,
    )

    agt_comb_exp = AssistantAgent(
        name="CombExp",
        system_message=sysmsgCombExp,
        model_client=llm_qwen3_30b,
        # model_client_stream=True,
        output_content_type=OutExtExp,
    )

    # Setup graph
    builder = DiGraphBuilder()
    builder.add_node(agt_ext_in_exp).add_node(agt_ext_res_exp).add_node(
        agt_ext_lkd_exp
    ).add_node(agt_comb_exp)

    # Add parallel edges

    builder.add_edge(agt_ext_in_exp, agt_ext_res_exp)
    builder.add_edge(agt_ext_in_exp, agt_ext_lkd_exp)
    # Add combination agent
    builder.add_edge(agt_ext_res_exp, agt_comb_exp)
    builder.add_edge(agt_ext_lkd_exp, agt_comb_exp)

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
