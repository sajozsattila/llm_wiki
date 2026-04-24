import streamlit as st
import re
import datetime
import json
import json5
import asyncio
import sys
from typing import Any, Dict, List, Optional, Annotated, TypedDict
import mlx.core as mx
import gc

# IMPORTANT: separate imports
from mlx_lm import load as mlx_lm_load, stream_generate, sample_utils
from mlx_vlm import load as mlx_vlm_load, generate as vlm_generate
from mlx_vlm.prompt_utils import apply_chat_template as vlm_apply_chat_template
from mlx_vlm.utils import load_config as vlm_load_config

import logging
logging.getLogger("transformers").setLevel(logging.ERROR)

from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    BaseMessage,
)

from langchain_core.tools import tool


# =========================
# MODEL TYPE DETECTION
# =========================
def is_vlm_model(model_name: str) -> bool:
    return "gemma" in model_name.lower()


# =========================
# MODEL CACHE
# =========================
def load_model_cached(model_name):
    if is_vlm_model(model_name):
        model, processor = mlx_vlm_load(model_name)
        config = vlm_load_config(model_name)
        return {
            "type": "vlm",
            "model": model,
            "processor": processor,
            "config": config,
        }
    else:
        model, tokenizer = mlx_lm_load(model_name)
        return {
            "type": "lm",
            "model": model,
            "tokenizer": tokenizer,
        }


# =========================
# Message Conversion
# =========================
def openai_to_langchain_messages(messages: List[Dict[str, Any]]) -> List[BaseMessage]:
    lc_messages: List[BaseMessage] = []

    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")

        if role == "user":
            lc_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            lc_messages.append(AIMessage(content=content))
        elif role == "system":
            lc_messages.append(SystemMessage(content=content))
        elif role == "tool":
            lc_messages.append(ToolMessage(content=content, tool_call_id="manual"))

    return lc_messages


def lc_to_hf_messages(messages: List[BaseMessage]) -> List[Dict[str, str]]:
    hf_messages = []

    for msg in messages:
        if isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, SystemMessage):
            role = "system"
        else:
            role = "assistant"

        hf_messages.append({
            "role": role,
            "content": msg.content or ""
        })

    return hf_messages

# =========================
# Robust JSON Parser
# =========================
def parse_json_robust(text: str) -> Optional[Dict]:
    """
    Robustly extract and parse JSON from LLM response text.
    Uses multiple strategies with json5 for maximum compatibility.

    Strategies (in order):
    1. Direct parsing with json5 (if entire text is valid JSON5)
    2. Extract last {...} block with regex, then parse with json5
    3. Extract first {...} block with regex, then parse with json5
    4. Clean prefix/suffix and parse with json5

    Args:
        text: Raw LLM response text (may contain explanation text before/after JSON)

    Returns:
        Parsed JSON dict if successful, None otherwise
    """

    # Strategy 1: Direct parsing with json5
    # (if the entire response is valid JSON5, no need to extract)
    try:
        return json5.loads(text)
    except ValueError:
        pass

    # Strategy 2: Extract last {...} block (most reliable)
    # This matches the last JSON-like block before end of string
    match = re.search(r"\{.*?\}(?=\s*$)", text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json5.loads(json_str)
        except ValueError:
            pass

    # Strategy 3: Extract first {...} block (fallback)
    # This matches the first JSON-like block (in case last one is malformed)
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json5.loads(json_str)
        except ValueError:
            pass

    # Strategy 4: Clean prefix/suffix and parse
    # Remove everything before first { and after last }
    cleaned = re.sub(r'^[^{]*', '', text)  # Remove prefix
    cleaned = re.sub(r'[^}]*$', '', cleaned)  # Remove suffix

    cleaned = cleaned.strip()
    if cleaned:
        try:
            return json5.loads(cleaned)
        except ValueError:
            pass

    # All strategies failed
    return None



# =========================
# MODEL CALL (UNIFIED)
# =========================
def call_model(messages, AVAILABLE_MODELS):
    model_name = AVAILABLE_MODELS[st.session_state.selected_model]
    model_bundle = load_model_cached(model_name)

    try:
        # =========================
        # TEXT MODEL (mlx_lm)
        # =========================
        if model_bundle["type"] == "lm":
            model = model_bundle["model"]
            tokenizer = model_bundle["tokenizer"]

            sampler = sample_utils.make_sampler(
                temp=st.session_state.temperature,
                top_p=st.session_state.top_p
            )

            hf_messages = lc_to_hf_messages(messages)

            prompt = tokenizer.apply_chat_template(
                hf_messages,
                tokenize=False,
                add_generation_prompt=True,
            )

            output = ""
            for r in stream_generate(
                model,
                tokenizer,
                prompt=prompt,
                max_tokens=4096,
                sampler=sampler,
            ):
                output += r.text

            return output

        # =========================
        # VISION MODEL (mlx_vlm)
        # =========================
        elif model_bundle["type"] == "vlm":
            model = model_bundle["model"]
            processor = model_bundle["processor"]
            config = model_bundle["config"]

            hf_messages = lc_to_hf_messages(messages)

            # Merge messages into single prompt
            prompt_text = "\n".join([m["content"] for m in hf_messages])

            # Check if frontend passed image(s)
            images = st.session_state.get("images", None)

            if images:
                formatted_prompt = vlm_apply_chat_template(
                    processor,
                    config,
                    prompt_text,
                    num_images=len(images),
                )

                result = vlm_generate(
                    model,
                    processor,
                    formatted_prompt,
                    images,
                    max_tokens=4096
                )

                # extract text from GenerationResult
                if hasattr(result, "text"):
                    output = result.text
                else:
                    output = str(result)
            else:
                # fallback to text-only usage of VLM
                formatted_prompt = vlm_apply_chat_template(
                    processor,
                    config,
                    prompt_text,
                    num_images=0,
                )

                result = vlm_generate(
                    model,
                    processor,
                    formatted_prompt,
                    images,
                    max_tokens=2048
                )

                # extract text from GenerationResult
                if hasattr(result, "text"):
                    output = result.text
                else:
                    output = str(result)

            return output
    finally:
        # Explicitly release all model references
        del model_bundle
        gc.collect()
        mx.metal.clear_cache()  # Frees MLX Metal memory buffer

# =========================
# Tools
# =========================
# wiki_search_tool.py
from opencode_agent_sdk import SDKClient, AgentOptions, AssistantMessage, TextBlock
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState

WIKI_DIR = "./wiki"


async def _run_wiki_search(search_query: str) -> str:
    """Uses opencode-agent-sdk to intelligently search the wiki directory."""
    print(f"Searching Wiki directory. Query: {search_query}")
    options = AgentOptions(
        model="mlx-community/gemma-4-e4b-it-4bit",
        server_url="http://127.0.0.1:4096",
        cwd=WIKI_DIR,
        system_prompt=(
            "You are a wiki search engine. The current directory contains markdown "
            "wiki pages. Search, read, and synthesize information to answer queries. "
            "Do NOT create or edit files. Return a structured answer with source filenames."
        ),
        allowed_tools=['glob', 'grep', 'Read', 'Bash'],
    )

    prompt = f"""Search the wiki for: "{search_query}"

    Steps:
    1. List available wiki pages (ls or find *.md)
    2. Search for relevant content (grep -r or read promising files)
    3. Synthesize a clear answer with citations (filename + excerpt)
    """

    result_parts = []

    client = SDKClient(options=options)
    await client.connect()
    try:
        await client.query(prompt)
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        result_parts.append(block.text)
    finally:
        await client.disconnect()

    return "\n".join(result_parts)


@tool
def wiki_search(query: str) -> str:
    """Search the LLM wiki knowledge base for information."""
    return asyncio.run(_run_wiki_search(query))

# =========================
# No more tool call
# =========================
def generate_final_answer(state):
    if state["agent_calls"] >= state["max_tool_calls"]:
        state["messages"].append(
            AIMessage((
                "The maximum number of agent calls has been excluded. "
                "Generate the final answer now, "
                "ensuring no further tool calls are made and basing the response only on the previously collected data."
            ))
        )

    return state["messages"]

# =========================
# State
# =========================
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    output: Optional[str]
    agent_calls: int
    confidence: float
    enough_info: bool
    max_tool_calls: int
    wiki_search_history: set  # Set of queries that have already been searched (doesn't count against limit)


# =========================
# System Prompt
# =========================
system_instruction = """You are a highly capable and careful reasoning agent. Your primary goal is to assist the user by providing accurate, well-supported answers.

You MUST follow EXACTLY one of these formats when you need to use a tool or conclude the conversation:

--- TOOL USE ---
{
  "action": "wiki_search",
  "input": "<query>"
}

--- FINAL ANSWER ---
{
  "final_answer": "<answer>",
  "confidence": "<number between 0 and 1>"
}

Decision Rules:
2. Use a tool (wiki_search) if the information required to answer the user's request is unknown or requires external data.
3. Do NOT use a tool if you already possess all necessary information to provide a complete answer.
4. Only provide a final answer with high confidence if the conclusion is strongly supported by the context or tool results.
"""


# =========================
# Confidence Extraction
# =========================
def extract_confidence(text: str) -> float:
    match = re.search(r"\"confidence\":\s*(\d+\.\d+)", text)
    if match:
        try:
            return float(match.group(1))
        except:
            return 0.0
    return 0.0


# =========================
# Confidence Verification
# =========================
def verify_confidence(state: AgentState) -> bool:

    if state["agent_calls"] == 0:
        return False

    if state["agent_calls"] == 1 and state["confidence"] < 0.9:
        return False

    return True


# =========================
# Agent Node
# =========================
def agent_node(state: AgentState, AVAILABLE_MODELS):

    if state["enough_info"]:
        return state

    response = call_model(state["messages"], AVAILABLE_MODELS)

    if state["agent_calls"] >= state["max_tool_calls"]:
        state["enough_info"] = True
        state["messages"].append(AIMessage(content=response))
        return state

    state["output"] = response
    state["confidence"] = extract_confidence(response)

    # --- NEW: Use robust JSON parser ---
    parsed_response = parse_json_robust(response)

    if parsed_response:
        action = parsed_response.get("action")
        input_data = parsed_response.get("input")

        # =========================
        # TOOL HANDLING
        # =========================
        if action in ["wiki_search", ]:
            # add the tool calling to the msg
            state["messages"].append(AIMessage(content=response))

            if action == "wiki_search":
                # validate tool input
                if not isinstance(input_data, str) or not input_data.strip():
                    state["messages"].append(
                        AIMessage(content="Invalid tool input. Please provide a valid search query.")
                    )
                    return state
                tool_input = input_data

                # Prevent duplicate searches
                if tool_input in state["wiki_search_history"]:
                    state["messages"].append(
                        AIMessage(
                            content=f"Note: The query '{tool_input}' was already searched in this conversation. Please provide a new query."
                        )
                    )
                    return state

                result = wiki_search.invoke({"query": tool_input})

                state["wiki_search_history"].add(tool_input)
                state["agent_calls"] += 1

                state["messages"].append(
                    ToolMessage(content=result, tool_call_id=f"manual{state["agent_calls"]}")
                )
                state["messages"] = generate_final_answer(state)
                return state


        # =========================
        # FINAL ANSWER
        # =========================
        if "final_answer" in parsed_response:
            state["enough_info"] = True
            state["messages"].append(AIMessage(content=response))
            return state

    # =========================
    # FALLBACK (non-JSON or failed parsing)
    # =========================
    state["enough_info"] = True
    state["messages"].append(AIMessage(content=response))
    return state


# =========================
# Decision Node
# =========================
def decide(state: AgentState):

    if state["enough_info"]:
        return "end"

    # if equal we still a last itteration to generate the final answer
    if state["agent_calls"] > state["max_tool_calls"]:
        return "end"

    return "agent"


# =========================
# Graph Builder
# =========================
def build_graph(AVAILABLE_MODELS):

    graph = StateGraph(AgentState)

    graph.add_node(
        "agent",
        lambda state: agent_node(state, AVAILABLE_MODELS),
    )

    graph.add_edge(START, "agent")

    graph.add_conditional_edges(
        "agent",
        decide,
        {
            "agent": "agent",
            "end": END,
        },
    )

    return graph.compile()


# =========================
# Run Agent
# =========================
def run_agent(frontend_messages, MAX_TOOL_CALLS, AVAILABLE_MODELS):

    graph = build_graph(AVAILABLE_MODELS)

    messages = (
            [SystemMessage(content=system_instruction)] +
            openai_to_langchain_messages(frontend_messages)
    )

    # add timestamp to the question so Agent will know if it is needs
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    messages[-1].content = f"msg timestamp: {timestamp_str}\n\n{messages[-1].content}"

    state: AgentState = {
        "messages": messages,
        "output": None,
        "agent_calls": 0,
        "confidence": 0.0,
        "enough_info": False,
        "max_tool_calls": MAX_TOOL_CALLS,
        "wiki_search_history": set(),  # Track searched queries (doesn't count against limit)
    }

    result = graph.invoke(state)

    output = result["output"] or ""

    # Check for structured final answer
    # Use robust JSON parser
    parsed_output = parse_json_robust(output)

    if parsed_output and "final_answer" in parsed_output:
        return parsed_output["final_answer"].strip()

    # Fallback to raw output if no JSON found or no final_answer key
    return output
