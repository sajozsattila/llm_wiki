# Wiki Graph Agent

## Project Goal

Transform the LLM Wiki into a **LangGraph subgraph** that serves as an intelligent knowledge base, replacing traditional RAG systems. The wiki's interconnected pages become a navigable knowledge graph where the agent can:
- Receive queries from the main LangGraph agent
- Flow through wiki links to collect relevant information
- Synthesize answers from multiple sources
- Return context-rich responses to the main graph

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        MAIN GRAPH                               │
│  ┌─────────┐    ┌──────────────┐    ┌──────────────────────┐    │
│  │  User   │───▶│ Router node  │───▶│    Wiki Subgraph     │    │
│  └─────────┘    └──────────────┘    │   ┌─────────────┐    │    │
│                     │               │──▶│ Query       │    │    │
│                     │               │   │ WikiNode    │    │    │
│                     │               │   │ Synthesize  │    │    │
│                     ▼               │   └────┬────────┘    │    │
│              ┌──────────────┐       │        │             │    │
│              │ Tools/Other  │──────▶│◀───────┘             │    │
│              └──────────────┘       │                      │    │
│                                     ▼                      │    │
│                              ┌─────────────┐               │    │
│                              │   Answer    │───────────────┘    │
│                              └─────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

## Wiki Subgraph Specification

### Nodes

1. **query_node**
   - Input: Raw query from main graph or user
   - Function: Parse and refine the question
   - Output: Structured search intent

2. **wiki_traverse**
   - Input: Search intent + current context
   - Function: Navigate wiki pages following [[links]]
   - Output: Collected relevant passages

3. **synthesize**
   - Input: Collected passages + original query
   - Function: Generate answer from gathered context
   - Output: Final answer + sources

### Edges

```
query_node ──▶ wiki_traverse ──▶ synthesize ──▶ END
```

### Conditional Edges

#### From query_node

- If query is ambiguous → **clarify** (ask user for more details)
- If query is clear → **wiki_traverse**

#### From wiki_traverse

- **traverse_more**: If more relevant pages exist → continue traversing
- **sufficient**: If enough information collected → **synthesize**

### State Management

```python
class WikiState(TypedDict):
    query: str
    search_intent: dict
    visited_pages: list[str]
    collected_context: list[dict]
    sources: list[str]
    answer: str
    should_continue: bool
```

### Node Functions

```python
def query_node(state: WikiState) -> WikiState:
    """Parse and refine the user's query."""
    query = state["query"]
    # Extract key concepts, entities
    search_intent = {
        "concepts": extract_concepts(query),
        "entity_types": extract_entity_types(query),
        "required_pages": identify_starting_pages(query),
    }
    return {"search_intent": search_intent}


def wiki_traverse(state: WikiState) -> WikiState:
    """Navigate wiki links to collect information."""
    intent = state["search_intent"]
    visited = state["visited_pages"]
    context = state["collected_context"]

    current_pages = find_starting_pages(intent["required_pages"])
    for page in current_pages:
        if page not in visited:
            content = read_wiki_page(page)
            relevant = extract_relevant(content, intent)
            context.append({"page": page, "content": relevant})
            # Follow wiki links to related pages
            related = extract_links(content)
            current_pages.extend(related)
        visited.append(page)

    # Check if we have enough context
    enough = len(context) >= MIN_CONTEXT_LENGTH

    return {
        "visited_pages": visited,
        "collected_context": context,
        "should_continue": not enough,
    }


def should_continue_traversal(state: WikiState) -> str:
    """Determine if more traversal is needed."""
    if state["should_continue"]:
        return "traverse_more"
    return "synthesize"


def synthesize(state: WikiState) -> WikiState:
    """Generate final answer from collected context."""
    context = state["collected_context"]
    query = state["query"]

    answer = generate_answer(query, context)
    sources = [c["page"] for c in context]

    return {"answer": answer, "sources": sources}
```

## Graph Construction

```python
from langgraph.graph import StateGraph, END

# Create subgraph
wiki_graph = StateGraph(WikiState)

# Add nodes
wiki_graph.add_node("query_node", query_node)
wiki_graph.add_node("wiki_traverse", wiki_traverse)
wiki_graph.add_node("synthesize", synthesize)

# Add edges
wiki_graph.add_edge("query_node", "wiki_traverse")
wiki_graph.add_edge("synthesize", END)

# Conditional edge from wiki_traverse
wiki_graph.add_conditional_edges(
    "wiki_traverse",
    should_continue_traversal,
    {
        "traverse_more": "wiki_traverse",  # Loop back
        "synthesize": "synthesize",
    },
)

# Set entry point
wiki_graph.set_entry_point("query_node")

# Compile subgraph
wiki_subgraph = wiki_graph.compile()
```

## Integration with Main Graph

```python
from langgraph.prebuilt import ToolNode

# Main graph uses wiki as a tool or subgraph
def router(state: MainState) -> str:
    """Route to appropriate handler."""
    query = state["query"]

    if is_wiki_related(query):
        return "wiki_subgraph"
    elif requires_tools(query):
        return "tools"
    else:
        return "general"


# Main graph definition
main_graph = StateGraph(MainState)
main_graph.add_node("router", router)
main_graph.add_node("wiki_subgraph", wiki_subgraph)
main_graph.add_node("tools", tool_node)

main_graph.add_conditional_edges(
    "router",
    router,
    {"wiki_subgraph": "wiki_subgraph", "tools": "tools"}
)
```

## Key Design Decisions

1. **Traverse vs Search**: Use wiki's natural link structure for traversal instead of chunk-level similarity search
2. **Context Accumulation**: Collect context over multiple hops rather than single-pass retrieval
3. **Source Tracking**: Always track which wiki pages contributed to the answer
4. **Looping**: Allow multiple traversal iterations until sufficient context is gathered
5. **Subgraph Isolation**: Wiki logic is encapsulated for reusability and testing

## Environment Variables

```
WIKI_PATH=./wiki
MIN_CONTEXT_LENGTH=2
MAX_HOPS=5
LLM_MODEL=mlx-community/llama-3.2-1b-instruct-4bit
```

## Testing

Run all tests:

```bash
# Unit tests for utils.py
python -m pytest test/test_utils.py -v

# Integration tests
python -m pytest test/test_integration.py -v

# All tests
python -m pytest test/ -v
```

Test scenarios:

1. **Query CAN be answered**: Questions that match wiki content
   - "What is a neural network?"
   - "What is forward propagation?"
   - "What is seq2seq?"

2. **Query CANNOT be answered**: Questions not in wiki
   - "What is quantum computing?" (wiki has neural networks, not quantum)
   - "Tell me about alien life on Mars"

### Running main.py

```bash
# Single query
python main.py "What is a neural network?"

# Interactive mode
python main.py -i
```