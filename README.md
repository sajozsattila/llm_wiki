# 🧠 LLM Wiki Agent: Advanced Knowledge Retrieval System

[![Status](https://img.shields.io/badge/Status-Prototype-blue.svg)](https://github.com/your-repo/your-repo)
[![Architecture](https://img.shields.io/badge/Architecture-LLM%20Wiki%20via%20LangGraph-orange.svg)](#architecture)

This project implements a sophisticated knowledge retrieval system that moves beyond standard Retrieval-Augmented Generation (RAG). By modeling the knowledge search as a **bounded, navigable subgraph** within a larger LangGraph agent, we transform retrieval into a form of automated, multi-step reasoning.

## 🚀 Overview: Why LLM Wiki vs. RAG?

Traditional RAG performs a single lookup: *Find chunks $\rightarrow$ Answer*.

The **LLM Wiki Agent** performs a *research journey*: *Navigate $\rightarrow$ Synthesize $\rightarrow$ Conclude*.

This system treats the knowledge base (`wiki/`) not as a static database, but as a navigable map. The Agent doesn't just retrieves; it *researches* the answer by following links between synthesized knowledge pages.

## 🏗️ Architecture: The Two-Graph System

The system is composed of two interacting, bounded LangGraph instances:

1.  **The Main Graph (The Conductor):** The high-level orchestrator. It manages the overall goal, decides *when* to search, and synthesizes the final answer.
2.  **The Subgraph Graph (The Explorer):** The low-level worker. It handles the bounded, iterative traversal of the knowledge base pages.

### 🧭 Flow Diagram (Conceptual)

**[Main Graph]** $\xrightarrow{\text{Search Needed?}}$ **[Subgraph Graph]** $\xrightarrow{\text{Returns Journey}}$ **[Main Graph]** $\xrightarrow{\text{Final Answer}}$ **User**

## 📂 Project Structure

The file structure mirrors the functional separation:

```
 .
 ├── raw/ # Immutable source documents (The Ground Truth) 
 │ ├── doc_a.pdf
 │ └── meeting_notes_v1.md
 ├── wiki/ # Synthesized knowledge base (The Navigable Map)
 │ ├── page_A.md # High-quality, curated article
 │ ├── page_B.md # Links to A, contains context needed for X
 │ └── page_C.md # Links to B, contains final piece of the puzzle
 ├── CLAUDE.md # System Instructions for the Claude Code (The Meta-Prompt)
 └── wikigraph.py # Contains both MainGraph and Subgraph implementations
```

## ⚙️ Technical Deep Dive: The Roles

### 🧭 The Subgraph (Explorer) - The Search Worker

*   **Goal:** To answer the question: "What pages do I need to visit, and in what order, to answer the `goal_query`?"
*   **Mechanism:** It loops (`READ_PAGE` $\rightarrow$ `DECIDE` $\rightarrow$ `READ_PAGE`) until the `action_instruction` becomes `"CONCLUSION_FOUND"`.
*   **Key Feature:** The `visited_pages` list is the **Guardrail** against infinite loops.

### 🧭 The Main Graph (Conductor) - The Orchestrator

*   **Goal:** To manage the overall process and ensure termination.
*   **Key Feature:** It treats the Subgraph execution as a single, complex "Tool Call." It doesn't care *how* the Subgraph found the answer, only *that* it found it and what the resulting `subgraph_thought_chain` is.

## ▶️ How to Run (Local Development)

1.  **Setup:** Ensure all dependencies (`langgraph`, LLM provider SDK) are installed.
2.  **Initialization:** Run `full_llm_wiki_system_integrated.py`.
3.  **Execution:** The script simulates the flow:
    *   `analyze_query` runs.
    *   `run_subgraph` executes the bounded loop (Explorer).
    *   `synthesize_answer` generates the final output based on the journey.

---