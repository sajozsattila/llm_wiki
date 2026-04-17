# full_llm_wiki_system_integrated.py

from typing import TypedDict, Annotated, Sequence, Any, List
from langgraph.graph import StateGraph, END

# =============================================================================
# 🌐 SHARED STATE DEFINITIONS
# =============================================================================

# --- Main Graph State (The Conductor) ---
class MainAgentState(TypedDict):
    original_query: str
    conductor_thought: str
    subgraph_thought_chain: str
    search_in_progress: bool

# --- Subgraph Graph State (The Explorer) ---
class SubgraphState(TypedDict):
    goal_query: str
    current_page_content: str
    visited_pages: List[str]
    action_instruction: str

# =============================================================================
# PART 1: THE SUBGRAPH GRAPH (The Explorer)
# =============================================================================

# --- Subgraph Nodes ---

def subgraph_read_page(state: SubgraphState) -> dict:
    """Simulates reading a page and deciding the next step."""
    print("\n--- [SUBGRAPH] Executing: Reading Page ---")
    # Simulation: We simulate a successful traversal of 3 pages.
    if len(state["visited_pages"]) < 3:
        next_page = "wiki/page_B.md"
        # The LLM synthesizes the content found on this page.
        summary = f"Page {len(state['visited_pages'])} read. Found context on X. Next page needed: {next_page}"
        return {"action_instruction": f"Go to {next_page}", "current_page_content": summary}
    else:
        # Termination condition met after 3 pages
        return {"action_instruction": "CONCLUSION_FOUND", "current_page_content": "All necessary context gathered."}

def subgraph_decide_next_step(state: SubgraphState) -> str:
    """Decides whether the search loop continues or terminates."""
    print("\n--- [SUBGRAPH] Executing: Deciding Next Step ---")
    if state["action_instruction"] == "CONCLUSION_FOUND":
        return "END_SUBGRAPH" # Signal to terminate the Subgraph
    else:
        # If we have a valid instruction, loop back to read the next page.
        return "READ_PAGE" # Signal to continue the loop

# --- Subgraph Graph Construction ---
subgraph_graph = StateGraph(SubgraphState)
subgraph_graph.add_node("READ_PAGE", subgraph_read_page)
subgraph_graph.add_node("DECIDE", subgraph_decide_next_step)

# Define the loop structure
subgraph_graph.add_edge("READ_PAGE", "DECIDE")
# Conditional Edge: The loop back
subgraph_graph.add_conditional_edges(
    "DECIDE",
    lambda state: "READ_PAGE" if state["action_instruction"] != "CONCLUSION_FOUND" else "END_SUBGRAPH",
)
# Termination Edge
subgraph_graph.add_edge("READ_PAGE", "DECIDE") # Ensure flow if needed

# Set the entry point
subgraph_graph.set_entry_point("READ_PAGE")


# --- Subgraph Execution Wrapper ---
def execute_subgraph_run(initial_query: str) -> str:
    """
    Runs the SubgraphGraph instance to completion and returns the final chain.
    """
    print("\n" + "="*70)
    print("🚀 EXECUTING SUBGRAPH (The Explorer is running its bounded loop)...")
    print("="*70)

    # --- SIMULATION OF SUBGRAPH RUN ---
    # In a real app, you would compile and invoke the subgraph_graph here.
    # We simulate the successful traversal:
    initial_state = SubgraphState(
        goal_query=initial_query,
        current_page_content="",
        visited_pages=["wiki/page_A.md"],
        action_instruction="READ_NEXT"
    )

    # Simulate the loop running until it hits the conclusion
    # (This simulates the subgraph_graph.invoke(initial_state))

    # The final output from the successful traversal:
    final_chain = "Thought Chain: Successfully navigated Page A -> Page B -> Page C. Relationship between X and Y is established."
    print("\n" + "="*70)
    print("✅ SUBGRAPH TRAVERSAL COMPLETE. Returning chain to Main Graph.")
    print("="*70)
    return final_chain


# =============================================================================
# 🧠 PART 2: THE MAIN GRAPH (The Conductor)
# =============================================================================

# --- Main Graph Nodes ---

def analyze_query(state: MainAgentState) -> dict:
    """Determines if the search is needed."""
    print("\n" + "="*50)
    print("🧠 MAIN NODE: Analyzing Query.")
    # For this test, we assume the query is complex and requires search.
    return {"conductor_thought": "Search required. Proceeding to Explorer."}

def run_subgraph_main_graph(state: MainAgentState) -> dict:
    """Delegates the search to the Subgraph and captures the result."""
    print("\n" + "="*50)
    print("🧠 MAIN NODE: Delegating Search to Subgraph...")

    # Call the function that runs the Subgraph instance
    chain = execute_subgraph_run(state["original_query"])

    # Return the result to be passed to the next node
    return {"subgraph_thought_chain": chain}

def synthesize_answer(state: MainAgentState) -> dict:
    """Writes the final answer based on the journey."""
    print("\n" + "="*50)
    print("🧠 MAIN NODE: Synthesizing Final Answer.")
    # The LLM uses the chain to write the final response.
    return {"conductor_thought": "Final Answer: Based on the journey, X relates to Y through the sequence found in Page B and Page C."}


# --- Main Graph Execution ---
if __name__ == "__main__":

    # --- Simulation Run ---

    # 1. Initial State
    initial_state = MainAgentState(
        original_query="Mi a visszajátszás?",
        conductor_thought="",
        subgraph_thought_chain="",
        search_in_progress=True
    )

    # --- EXECUTION SEQUENCE ---

    # Step 1: Analyze (Main Graph)
    state_after_analyze = analyze_query(initial_state)

    # Step 2: Run Subgraph (Main Graph calls the Explorer)
    state_after_search = run_subgraph_main_graph(
        {**initial_state, "conductor_thought": state_after_analyze["conductor_thought"]}
    )

    # Step 3: Synthesize (Main Graph)
    final_state = synthesize_answer(
        {**initial_state, "conductor_thought": state_after_analyze["conductor_thought"], "subgraph_thought_chain": state_after_search["subgraph_thought_chain"]}
    )

    print("\n" + "="*70)
    print("✅ FULL LLM WIKI SYSTEM EXECUTION COMPLETE.")
    print("Final Conductor Thought:", final_state["conductor_thought"])
    print("="*70)