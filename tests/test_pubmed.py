# tests/test_pubmed.py

import unittest
from pubmed_fetcher.pubmed import search_and_fetch

class TestPubMedFetcher(unittest.TestCase):

    def test_search_and_fetch_returns_list(self):
        results = search_and_fetch("covid", retmax=2)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_result_has_expected_fields(self):
        results = search_and_fetch("cancer", retmax=1)
        self.assertTrue("title" in results[0])
        self.assertTrue("authors" in results[0])
        self.assertTrue("abstract" in results[0])

    def test_empty_query_returns_empty_list(self):
        results = search_and_fetch("aslkdhfalksdhfalksdhflkasdhf", retmax=1)
        self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()
