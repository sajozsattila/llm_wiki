#!/usr/bin/env python3
"""
Wiki Graph Agent - Main Entry Point

This script initializes the LangGraph wiki subgraph and accepts user queries.
Run with: python main.py
"""

import argparse
import sys

from graph import run_wiki_query, wiki_subgraph


def main():
    parser = argparse.ArgumentParser(description="Wiki Graph Agent")
    parser.add_argument("query", nargs="*", help="Question to ask the wiki")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    elif args.query:
        query = " ".join(args.query)
        run_query(query)
    else:
        parser.print_help()
        print("\nExamples:")
        print("  python main.py \"What is a neural network?\"")
        print("  python main.py -i")


def run_query(query: str):
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"{'='*60}\n")
    
    result = run_wiki_query(query)
    
    print(f"Answer:\n{result.get('answer', 'No answer generated')}\n")
    print(f"Sources: {result.get('sources', [])}\n")
    print(f"Visited pages: {result.get('visited_pages', [])}\n")
    
    return result


def interactive_mode():
    print("Wiki Graph Agent - Interactive Mode")
    print("Type 'quit' or 'exit' to exit\n")
    
    while True:
        try:
            query = input("Ask a question: ").strip()
            if not query:
                continue
            if query.lower() in ("quit", "exit"):
                print("Goodbye!")
                break
            
            run_query(query)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            break


if __name__ == "__main__":
    main()
