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
from common.constants import (
    deepR1_1b,
    deepR1_7b,
    deepR1_14b,
    deepR1_32b,
    gemma3_4b,
    gemma3_12b,
    gemma3qat_12b,
    llama32_1b,
    llama32fp16_3b,
    qwen3_30b,
)
from prompts.out_ext import OutComb

# Prompts specific
from prompts.sysmsg_ext import (
    sysmsgComb,
    sysmsgCombEdu,
    sysmsgCombExp,
    sysmsgExtLkdEdu,
    sysmsgExtLkdExp,
    sysmsgExtResEdu,
    sysmsgExtResExp,
)

# Clients setup
llm_qwen3_30b = set_model(**qwen3_30b)
# llm_llama32fp16_3b = set_model(**llama32fp16_3b)
llm_llama32_1b = set_model(**llama32_1b)
# llm_deepR1_1b = set_model(**deepR1_1b)
# llm_deepR1_7b = set_model(**deepR1_7b)
# llm_deepR1_14b = set_model(**deepR1_14b)
llm_deepR1_32b = set_model(**deepR1_32b)
# llm_gemma3_4b = set_model(**gemma3_4b)
# llm_gemma3_12b = set_model(**gemma3_12b)
# llm_gemma3qat_12b = set_model(**gemma3qat_12b)
# llm_qwen3_1_7b = set_model(**qwen3_1_7b)
eval_llm = llm_qwen3_30b
# eval_llm = llm_qwen3_1_7b


# Main
async def main():
    """
    1. Initial Input Agents
    """
    agt_ext_in_edu = AssistantAgent(
        name="ExtInEdu",
        system_message="You have one job. No matter what the user says, you will ALWAYS respond with the following exact phrase and nothing else: 'Please extract the education details from the markdown file'",
        model_client=llm_llama32_1b,
        model_client_stream=True,
    )
    agt_ext_in_exp = AssistantAgent(
        name="ExtInExp",
        system_message="You have one job. No matter what the user says, you will ALWAYS respond with the following exact phrase and nothing else: 'Please extract the work experience details from the markdown file'",
        model_client=llm_llama32_1b,
        model_client_stream=True,
    )

    """
    2. Resume Extraction Agents
    """
    agt_ext_res_edu = AssistantAgent(
        name="ExtResEdu",
        system_message=sysmsgExtResEdu,
        model_client=eval_llm,
        # model_client_stream=True,
        output_content_type=OutComb.OutExtEdu,
    )
    agt_ext_res_exp = AssistantAgent(
        name="ExtResExp",
        system_message=sysmsgExtResExp,
        model_client=eval_llm,
        model_client_stream=True,
        output_content_type=OutComb.OutExtExp,
    )

    """
    3. Linkedin Extraction Agents
    """
    agt_ext_lkd_edu = AssistantAgent(
        name="ExtLkdEdu",
        system_message=sysmsgExtLkdEdu,
        model_client=eval_llm,
        # model_client_stream=True,
        output_content_type=OutComb.OutExtEdu,
    )
    agt_ext_lkd_exp = AssistantAgent(
        name="ExtLkdExp",
        system_message=sysmsgExtLkdExp,
        model_client=llm_deepR1_32b,
        model_client_stream=True,
        output_content_type=OutComb.OutExtExp,
    )

    """
    4. Combination Agents
    """
    agt_comb_edu = AssistantAgent(
        name="CombEdu",
        system_message=sysmsgCombEdu,
        model_client=eval_llm,
        model_client_stream=True,
        output_content_type=OutComb.OutExtEdu,
    )

    agt_comb_exp = AssistantAgent(
        name="CombExp",
        system_message=sysmsgCombExp,
        model_client=llm_deepR1_32b,
        model_client_stream=True,
        output_content_type=OutComb.OutExtExp,
    )

    agt_comb = AssistantAgent(
        name="Comb",
        system_message=sysmsgComb,
        model_client=llm_deepR1_32b,
        model_client_stream=True,
        output_content_type=OutComb,
    )

    """
    5. Graph Setup -> Nodes
    """
    builder = DiGraphBuilder()

    # 5a. Input Nodes
    builder.add_node(agt_ext_in_edu).add_node(agt_ext_in_exp)

    # 5bi. Extraction Resume Nodes
    builder.add_node(agt_ext_res_edu).add_node(agt_ext_res_exp)

    # 5bii. Extraction Linkedin Nodes
    builder.add_node(agt_ext_lkd_edu).add_node(agt_ext_lkd_exp)

    # 5c. Combination Nodes
    builder.add_node(agt_comb_edu)
    builder.add_node(agt_comb_exp)
    builder.add_node(agt_comb)

    """
    6. Graph Flow -> Edges
    """
    # 6a. Input -> Extraction
    # i. Education
    builder.add_edge(agt_ext_in_edu, agt_ext_res_edu)
    builder.add_edge(agt_ext_in_edu, agt_ext_lkd_edu)

    # ii. Experience
    builder.add_edge(agt_ext_in_exp, agt_ext_res_exp)
    builder.add_edge(agt_ext_in_exp, agt_ext_lkd_exp)

    # 6b. Extraction -> Combination
    # i. Education
    builder.add_edge(agt_ext_res_edu, agt_comb_edu)
    builder.add_edge(agt_ext_lkd_edu, agt_comb_edu)

    # ii. Experience
    builder.add_edge(agt_ext_res_exp, agt_comb_exp)
    builder.add_edge(agt_ext_lkd_exp, agt_comb_exp)

    builder.add_edge(agt_comb_edu, agt_comb)
    builder.add_edge(agt_comb_exp, agt_comb)

    # 6. Define the flow of the graph
    flow = GraphFlow(participants=builder.get_participants(), graph=builder.build())

    # Trigger the flow with initial input
    await Console(flow.run_stream(task=f"Start the flow"), output_stats=True)

    # Cleanup and close models
    # await llm_qwen3_30b.close()
    await eval_llm.close()
    await llm_llama32_1b.close()


if __name__ == "__main__":
    asyncio.run(main())
