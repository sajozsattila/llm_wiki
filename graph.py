import os
import re
from typing import TypedDict

from mlx_vlm import generate as vlm_generate
from mlx_vlm.prompt_utils import apply_chat_template as vlm_apply_chat_template
from langgraph.graph import StateGraph, END

from utils import (
    WikiState,
    read_wiki_page,
    extract_wiki_links,
    extract_title,
    extract_summary,
    find_starting_pages,
    extract_relevant_passages,
    MIN_CONTEXT_LENGTH,
)


LLM_MODEL = os.environ.get("LLM_MODEL", "mlx-community/gemma-4-e4b-it-4bit")


def load_llm():
    from utils import load_model_cached
    return load_model_cached(LLM_MODEL)


llm_cache = None


def get_llm():
    global llm_cache
    if llm_cache is None:
        llm_cache = load_llm()
    return llm_cache


def generate_with_llm(prompt: str) -> str:
    model_data = get_llm()
    if model_data["type"] == "lm":
        model = model_data["model"]
        tokenizer = model_data["tokenizer"]
        from mlx_lm import stream_generate
        response = ""
        for token in stream_generate(model, tokenizer, prompt, max_tokens=200):
            if hasattr(token, 'token'):
                response += tokenizer.decode([token.token])
            elif hasattr(token, 'text'):
                response += token.text
            elif isinstance(token, str):
                response += token
            else:
                response += str(token)
        return response.strip()
    elif model_data["type"] == "vlm":
        model = model_data["model"]
        processor = model_data["processor"]
        config = model_data["config"]

        if hasattr(config, "seq_len"):
            max_tokens = min(200, config.seq_len)
        else:
            max_tokens = 200
        prompt_formatted = vlm_apply_chat_template(processor, config, prompt, role="user")
        result = vlm_generate(model, processor, prompt_formatted, max_tokens=max_tokens)
        return result.text.strip()
    return "LLM generation not supported for this model type"


def extract_concepts(query: str) -> list[str]:
    common_words = {"a", "an", "the", "is", "are", "was", "were", "be", "been",
                    "being", "have", "has", "had", "do", "does", "did", "will",
                    "would", "could", "should", "may", "might", "must", "shall",
                    "can", "need", "dare", "ought", "used", "to", "of", "in",
                    "for", "on", "with", "at", "by", "from", "as", "into",
                    "through", "during", "before", "after", "above", "below",
                    "between", "under", "again", "further", "then", "once",
                    "here", "there", "when", "where", "why", "how", "all",
                    "each", "few", "more", "most", "other", "some", "such",
                    "no", "nor", "not", "only", "own", "same", "so", "than",
                    "too", "very", "what", "which", "who", "whom", "this",
                    "that", "these", "those", "ami", "van", "az", "egy",
                    "nem", "és", "vagy", "de", "ha", "akkor", "mert", "mi",
                    "ki", "hol", "mikor", "miért", "hogy"}
    words = re.findall(r"\b[a-zA-ZáéíóúőüÖÜ]+\b", query.lower())
    return [w for w in words if w not in common_words and len(w) > 2]


def query_node(state: WikiState) -> WikiState:
    query = state["query"]
    concepts = extract_concepts(query)
    search_intent = {
        "concepts": concepts,
        "query": query,
    }
    return {"search_intent": search_intent}


def wiki_traverse(state: WikiState) -> WikiState:
    intent = state["search_intent"]
    visited = list(state.get("visited_pages", []))
    context = list(state.get("collected_context", []))
    max_hops = state.get("max_hops", 5)
    
    current_pages = find_starting_pages(intent.get("concepts", []))
    pages_to_visit = [p for p in current_pages if p not in visited]
    
    all_links = []
    remaining = max(0, max_hops - len(visited))
    for page in pages_to_visit[:remaining]:
        if page in visited:
            continue
        try:
            content = read_wiki_page(page)
            relevant = extract_relevant_passages(content, intent.get("query", ""))
            context.append({
                "page": page,
                "title": extract_title(content),
                "summary": extract_summary(content),
                "relevant": relevant,
            })
            links = extract_wiki_links(content)
            for link in links:
                if link not in visited and link not in all_links:
                    all_links.append(link)
        except FileNotFoundError:
            pass
        visited.append(page)
    
    for link in all_links[:remaining]:
        try:
            content = read_wiki_page(link)
            relevant = extract_relevant_passages(content, intent.get("query", ""))
            context.append({
                "page": link,
                "title": extract_title(content),
                "summary": extract_summary(content),
                "relevant": relevant,
            })
            visited.append(link)
        except FileNotFoundError:
            pass
    
    enough = len(context) >= MIN_CONTEXT_LENGTH or len(visited) >= max_hops
    return {
        "visited_pages": visited,
        "collected_context": context,
        "should_continue": not enough,
    }


def should_continue_traversal(state: WikiState) -> str:
    max_hops = state.get("max_hops", 5)
    if state.get("should_continue", False) and len(state.get("visited_pages", [])) < max_hops:
        return "traverse_more"
    return "synthesize"


def synthesize(state: WikiState) -> WikiState:
    context = state["collected_context"]
    query = state["query"]
    if not context:
        return {
            "answer": "No relevant information found in the wiki.",
            "sources": [],
            "fallback_needed": True,
            "fallback_reason": "no_context_found",
        }
    context_text = "\n\n".join([
        f"## {c.get('title', c['page'])}\n{c.get('summary', '')}\n" + "\n".join(c.get("relevant", []))
        for c in context
    ])
    prompt = f"""Based on the following wiki content, answer the user's question.

Question: {query}

Wiki Content:
{context_text}

Provide a concise answer based on the wiki content above. Cite the sources you used."""
    answer = generate_with_llm(prompt)
    sources = list(set([c["page"] for c in context]))
    
    no_info_phrase = any(phrase in answer.lower() for phrase in [
        "does not contain",
        "no relevant information",
        "no information found",
        "no information about",
    ])
    fallback_needed = no_info_phrase
    
    return {
        "answer": answer, 
        "sources": sources, 
        "fallback_needed": fallback_needed,
        "fallback_reason": "no_relevant_content" if fallback_needed else ""
    }


def create_wiki_graph():
    wiki_graph = StateGraph(WikiState)
    wiki_graph.add_node("query_node", query_node)
    wiki_graph.add_node("wiki_traverse", wiki_traverse)
    wiki_graph.add_node("synthesize", synthesize)
    wiki_graph.add_edge("query_node", "wiki_traverse")
    wiki_graph.add_conditional_edges(
        "wiki_traverse",
        should_continue_traversal,
        {
            "traverse_more": "wiki_traverse",
            "synthesize": "synthesize",
        },
    )
    wiki_graph.add_edge("synthesize", END)
    wiki_graph.set_entry_point("query_node")
    return wiki_graph.compile()


wiki_subgraph = create_wiki_graph()


def run_wiki_query(query: str, max_hops: int = 5) -> dict:
    initial_state: WikiState = {
        "query": query,
        "search_intent": {},
        "visited_pages": [],
        "collected_context": [],
        "sources": [],
        "answer": "",
        "should_continue": True,
        "max_hops": max_hops,
        "fallback_needed": False,
        "fallback_reason": "",
    }
    result = wiki_subgraph.invoke(initial_state)
    return result


class MainState(TypedDict):
    query: str
    wiki_result: dict
    raw_answer: str
    final_answer: str
    sources: list[str]


def router_node(state: MainState) -> MainState:
    query = state["query"]
    wiki_result = run_wiki_query(query)
    return {
        "wiki_result": wiki_result,
    }


def should_use_wiki_fallback(state: MainState) -> str:
    wiki_result = state.get("wiki_result", {})
    if wiki_result.get("fallback_needed", False):
        return "need_fallback"
    return "wiki_success"


def raw_synthesize_node(state: MainState) -> MainState:
    query = state["query"]
    prompt = f"""Answer the following question concisely:

Question: {query}

Provide a helpful and accurate answer."""
    answer = generate_with_llm(prompt)
    return {
        "raw_answer": answer,
    }


def finalize_answer(state: MainState) -> MainState:
    wiki_result = state.get("wiki_result", {})
    if wiki_result.get("fallback_needed", False):
        return {
            "final_answer": state.get("raw_answer", ""),
            "sources": [],
        }
    else:
        return {
            "final_answer": wiki_result.get("answer", ""),
            "sources": wiki_result.get("sources", []),
        }


def create_main_graph():
    main_graph = StateGraph(MainState)
    
    main_graph.add_node("router", router_node)
    main_graph.add_node("raw_synthesize", raw_synthesize_node)
    main_graph.add_node("finalize", finalize_answer)
    
    main_graph.add_conditional_edges(
        "router",
        should_use_wiki_fallback,
        {
            "need_fallback": "raw_synthesize",
            "wiki_success": "finalize",
        },
    )
    
    main_graph.add_edge("raw_synthesize", "finalize")
    main_graph.add_edge("finalize", END)
    
    main_graph.set_entry_point("router")
    return main_graph.compile()


main_subgraph = create_main_graph()


def run_main_query(query: str, max_hops: int = 5) -> dict:
    initial_state: MainState = {
        "query": query,
        "wiki_result": {},
        "raw_answer": "",
        "final_answer": "",
        "sources": [],
    }
    result = main_subgraph.invoke(initial_state)
    return result
