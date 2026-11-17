import unittest

from statute_retriever import retrieve_bns_statutes


class FakeGraph:
    def __init__(self):
        self.query_text = ""
        self.params = {}

    def query(self, query, params=None):
        self.query_text = query
        self.params = params or {}
        return [
            {
                "section_properties": {
                    "type": "Section",
                    "section": "318",
                    "name": "Cheating",
                    "summary": "Cheating and dishonestly inducing delivery of property",
                },
                "statute_properties": {
                    "type": "Statute",
                    "name": "Bharatiya Nyaya Sanhita, 2023",
                },
                "matched_keywords": ["cheating", "fraud"],
            }
        ]


class StatuteRetrieverTests(unittest.TestCase):
    def test_retrieval_uses_flexible_property_matching_and_category_terms(self):
        graph = FakeGraph()

        statutes = retrieve_bns_statutes(graph, "cyber_fraud_impersonation")

        self.assertIn("ANY(key IN keys(section)", graph.query_text)
        self.assertIn("toLower(toString(section[key])) CONTAINS keyword", graph.query_text)
        self.assertEqual(graph.params["statute_relationships"], ["PART_OF_STATUTE", "PART_OF_ACT", "PART_OF"])
        self.assertIn("personation", graph.params["keywords"])
        self.assertEqual(
            statutes,
            [
                {
                    "section": "318",
                    "title": "Cheating",
                    "statute": "Bharatiya Nyaya Sanhita, 2023",
                    "description": "Cheating and dishonestly inducing delivery of property",
                    "matched_keywords": ["cheating", "fraud"],
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
