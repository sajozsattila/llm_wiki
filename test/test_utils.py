import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestWikiFunctions(unittest.TestCase):
    def setUp(self):
        self.test_wiki_dir = tempfile.mkdtemp()
        self.test_wiki_path = Path(self.test_wiki_dir)
        
        self.neural_networks_content = """# Neural Networks Basics

**Summary**: Feedforward neural networks are the foundation of deep learning.

**Sources**: [[A Mesterséges Neurális Hálózat alapjai – 1. rész]]

---

## Network Architecture

A feedforward neural network consists of three layer types:
- **Input Layer**: Receives observed data
- **Hidden Layer**: Performs computations
- **Output Layer**: Produces the final prediction

## Related pages

- [[seq2seq]]
- [[recurrent-neural-networks]]
"""

        self.seq2seq_content = """# Seq2seq Models

**Summary**: Seq2seq models transform variable-length input sequences.

**Sources**: [[Autoregressziós seq2seq – 1. rész]]

---

## Architecture

Seq2seq uses an encoder-decoder architecture.

## Related pages

- [[neural-networks-basics]]
- [[lstm]]
"""

        (self.test_wiki_path / "neural-networks-basics.md").write_text(self.neural_networks_content)
        (self.test_wiki_path / "seq2seq.md").write_text(self.seq2seq_content)
        
        self.original_wiki_path = os.environ.get("WIKI_PATH")
        os.environ["WIKI_PATH"] = self.test_wiki_dir
        
        import importlib
        import utils as utils_module
        importlib.reload(utils_module)

    def tearDown(self):
        if self.original_wiki_path:
            os.environ["WIKI_PATH"] = self.original_wiki_path
        else:
            os.environ.pop("WIKI_PATH", None)
        
        import shutil
        shutil.rmtree(self.test_wiki_dir)

    def test_list_wiki_pages(self):
        from utils import list_wiki_pages
        pages = list_wiki_pages()
        self.assertEqual(len(pages), 2)
        self.assertIn("neural-networks-basics", pages)
        self.assertIn("seq2seq", pages)

    def test_read_wiki_page(self):
        from utils import read_wiki_page
        content = read_wiki_page("neural-networks-basics")
        self.assertIn("Neural Networks Basics", content)
        self.assertIn("Input Layer", content)

    def test_extract_wiki_links(self):
        from utils import extract_wiki_links
        links = extract_wiki_links(self.neural_networks_content)
        self.assertIn("A Mesterséges Neurális Hálózat alapjai – 1. rész", links)
        self.assertIn("seq2seq", links)
        self.assertIn("recurrent-neural-networks", links)

    def test_extract_title(self):
        from utils import extract_title
        title = extract_title(self.neural_networks_content)
        self.assertEqual(title, "Neural Networks Basics")

    def test_extract_summary(self):
        from utils import extract_summary
        summary = extract_summary(self.neural_networks_content)
        self.assertIn("Feedforward neural networks", summary)

    def test_find_starting_pages_with_keywords(self):
        from utils import find_starting_pages
        pages = find_starting_pages(["neural", "network"])
        self.assertIn("neural-networks-basics", pages)

    def test_find_starting_pages_no_match(self):
        from utils import find_starting_pages
        pages = find_starting_pages(["xyznonexistent"])
        self.assertGreaterEqual(len(pages), 1)

    def test_extract_relevant_passages(self):
        from utils import extract_relevant_passages
        passages = extract_relevant_passages(self.neural_networks_content, "hidden layer")
        self.assertTrue(len(passages) > 0)
        self.assertTrue(any("Hidden Layer" in p for p in passages))

    def test_wiki_state_typed_dict(self):
        from utils import WikiState
        state: WikiState = {
            "query": "test query",
            "search_intent": {"concepts": ["test"]},
            "visited_pages": ["page1"],
            "collected_context": [{"page": "page1", "content": "test"}],
            "sources": ["page1"],
            "answer": "test answer",
            "should_continue": False,
        }
        self.assertEqual(state["query"], "test query")
        self.assertFalse(state["should_continue"])


if __name__ == "__main__":
    unittest.main()
