import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestExtractConcepts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import langgraph
            cls.can_import = True
        except ImportError:
            cls.can_import = False

    def test_extract_concepts_english(self):
        if not self.can_import:
            self.skipTest("langgraph not installed")
        from graph import extract_concepts
        concepts = extract_concepts("What is a neural network?")
        self.assertIn("neural", concepts)
        self.assertIn("network", concepts)

    def test_extract_concepts_filters_common_words(self):
        if not self.can_import:
            self.skipTest("langgraph not installed")
        from graph import extract_concepts
        concepts = extract_concepts("What is the neural network?")
        self.assertNotIn("what", concepts)
        self.assertNotIn("is", concepts)
        self.assertNotIn("the", concepts)


class TestShouldContinueTraversal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import langgraph
            cls.can_import = True
        except ImportError:
            cls.can_import = False

    def test_should_continue_when_true(self):
        if not self.can_import:
            self.skipTest("langgraph not installed")
        from graph import should_continue_traversal
        state = {"should_continue": True, "visited_pages": ["page1"]}
        result = should_continue_traversal(state)
        self.assertEqual(result, "traverse_more")

    def test_should_synthesize_when_false(self):
        if not self.can_import:
            self.skipTest("langgraph not installed")
        from graph import should_continue_traversal
        state = {"should_continue": False, "visited_pages": ["page1"]}
        result = should_continue_traversal(state)
        self.assertEqual(result, "synthesize")


if __name__ == "__main__":
    unittest.main()
