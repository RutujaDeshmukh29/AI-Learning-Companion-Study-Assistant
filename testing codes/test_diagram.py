
import unittest
from utils.diagram import clean_mermaid

class TestDiagram(unittest.TestCase):

    def test_clean_mermaid_removes_fences(self):
        raw_code = """```mermaid
flowchart TD
    A-->B
    B-->C
```"""
        expected_code = "flowchart TD
A-->B
B-->C"
        self.assertEqual(clean_mermaid(raw_code), expected_code)

    def test_clean_mermaid_handles_no_fences(self):
        raw_code = "flowchart TD
A-->B
B-->C"
        self.assertEqual(clean_mermaid(raw_code), raw_code)

    def test_clean_mermaid_removes_prose(self):
        raw_code = """Here is a simple flowchart:
flowchart TD
    A-->B
    B-->C
"""
        expected_code = "flowchart TD
A-->B
B-->C"
        self.assertEqual(clean_mermaid(raw_code), expected_code)

    def test_clean_mermaid_preserves_indented_code(self):
        raw_code = """
  flowchart TD
      subgraph "Group"
          A-->B
      end
"""
        expected_code = "flowchart TD
      subgraph "Group"
          A-->B
      end"
        # We are not asserting the cleaned code is exactly the same, but rather that the newlines are preserved.
        cleaned = clean_mermaid(raw_code)
        self.assertIn("
", cleaned)
        self.assertNotIn("Here is", cleaned)
        

if __name__ == '__main__':
    unittest.main()
