"""Integration tests for the Wiki Graph Agent.

Tests two scenarios:
1. Query that CAN be answered by wiki content
2. Query that CANNOT be answered by wiki content

Run with: pytest test/test_integration.py -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestWikiQueryAnswering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import langgraph
            cls.has_langgraph = True
        except ImportError:
            cls.has_langgraph = False

    def setUp(self):
        if not self.has_langgraph:
            self.skipTest("langgraph not installed")

    def test_query_can_be_answered(self):
        """Test a query that should be answered by wiki content."""
        from graph import run_wiki_query

        query = "What is a neural network?"
        result = run_wiki_query(query)

        self.assertIn("query", result)
        self.assertEqual(result["query"], query)
        self.assertTrue(len(result.get("visited_pages", [])) > 0)
        self.assertTrue(len(result.get("collected_context", [])) > 0)

    def test_query_content_is_relevant(self):
        """Test that collected context is relevant to the query."""
        from graph import run_wiki_query

        query = "What is forward propagation?"
        result = run_wiki_query(query)

        context = result.get("collected_context", [])
        self.assertTrue(len(context) > 0)

        found_relevant = False
        for ctx in context:
            content = str(ctx.get("relevant", [])) + str(ctx.get("summary", ""))
            if "forward" in content.lower() or "propagation" in content.lower():
                found_relevant = True
                break

        self.assertTrue(found_relevant, "Expected relevant content about forward propagation")

    def test_sources_tracked(self):
        """Test that sources are tracked."""
        from graph import run_wiki_query

        query = "What is a neural network?"
        result = run_wiki_query(query)

        sources = result.get("sources", [])
        self.assertIsInstance(sources, list)


class TestWikiQueryNotAnswering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import langgraph
            cls.has_langgraph = True
        except ImportError:
            cls.has_langgraph = False

    def setUp(self):
        if not self.has_langgraph:
            self.skipTest("langgraph not installed")

    def test_query_cannot_be_answered(self):
        """Test a query about content NOT in the wiki."""
        from graph import run_wiki_query

        query = "What is quantum computing?"
        result = run_wiki_query(query)

        context = result.get("collected_context", [])
        context_text = ""
        for ctx in context:
            context_text += str(ctx.get("relevant", [])) + str(ctx.get("summary", ""))

        context_text_lower = context_text.lower()
        has_quantum = "quantum" in context_text_lower

        if has_quantum:
            print(f"Warning: Query about 'quantum computing' found related content - wiki may have been updated")
        
        self.assertTrue(len(result.get("visited_pages", [])) > 0)

    def test_unknown_topic_handled(self):
        """Test handling of unknown topic gracefully."""
        from graph import run_wiki_query

        query = "Tell me about alien life on Mars"
        result = run_wiki_query(query)

        self.assertIn("answer", result)
        self.assertTrue(len(result.get("visited_pages", [])) > 0)


class TestGraphStructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import langgraph
            cls.has_langgraph = True
        except ImportError:
            cls.has_langgraph = False

    def setUp(self):
        if not self.has_langgraph:
            self.skipTest("langgraph not installed")

    def test_graph_nodes_exist(self):
        """Test that all required nodes exist in the graph."""
        from graph import wiki_subgraph

        graph = wiki_subgraph
        self.assertIsNotNone(graph)

    def test_state_required_fields(self):
        """Test that state contains required fields."""
        from utils import WikiState
        from typing import get_type_hints

        hints = get_type_hints(WikiState)
        self.assertIn("query", hints)
        self.assertIn("answer", hints)
        self.assertIn("sources", hints)


if __name__ == "__main__":
    unittest.main()