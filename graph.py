import os
import re
from typing import TypedDict

from langgraph.graph import StateGraph, END

from utils import (
    WikiState,
    get_wiki_path,
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
                    "that", "these", "those", "ami", "van", "a", "az", "egy",
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
    for page in pages_to_visit[:max_hops - len(visited)]:
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
    
    for link in all_links[:max_hops - len(visited)]:
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
    sources = [c["page"] for c in context]
    return {"answer": answer, "sources": sources}


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
    }
    result = wiki_subgraph.invoke(initial_state)
    return result
