import unittest
from src.graph import build_graph_bfs_recursive, reverse_dependencies, load_test_graph


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.graph = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": ["A"],  # цикл
        }

    def test_bfs_and_cycle(self):
        result = build_graph_bfs_recursive("A", lambda x: self.graph.get(x, []), 5)
        self.assertEqual(set(result), {"A", "B", "C", "D"})

    def test_max_depth(self):
        result = build_graph_bfs_recursive("A", lambda x: self.graph.get(x, []), 1)
        self.assertEqual(result, {"A": ["B", "C"], "B": [], "C": []})

    def test_reverse(self):
        result = build_graph_bfs_recursive("A", lambda x: self.graph.get(x, []), 5)
        self.assertEqual(reverse_dependencies(result, "A"), ["B", "C", "D"])


if __name__ == "__main__":
    unittest.main()
