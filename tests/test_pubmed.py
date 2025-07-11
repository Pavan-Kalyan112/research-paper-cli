import pytest
from unittest.mock import patch, MagicMock
from pubmed_fetcher import pubmed

# Sample XML response simulating PubMed XML
SAMPLE_XML = """
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <Article>
        <ArticleTitle>Sample Research Title</ArticleTitle>
        <Abstract>
          <AbstractText>This is a sample abstract for testing.</AbstractText>
        </Abstract>
        <AuthorList>
          <Author>
            <LastName>Doe</LastName>
            <ForeName>John</ForeName>
            <AffiliationInfo>
              <Affiliation>Pfizer Inc., New York, USA</Affiliation>
            </AffiliationInfo>
          </Author>
        </AuthorList>
        <Journal>
          <JournalIssue>
            <PubDate>
              <Year>2023</Year>
            </PubDate>
          </JournalIssue>
        </Journal>
      </Article>
    </MedlineCitation>
  </PubmedArticle>
</PubmedArticleSet>
"""

# -------------------------------
# Test parse_pubmed_xml directly
# -------------------------------
def test_parse_pubmed_xml_basic():
    idlist = ["12345678"]
    results = pubmed.parse_pubmed_xml(SAMPLE_XML, idlist)
    
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["PubmedID"] == "12345678"
    assert "Pfizer" in results[0]["CompanyAffiliation(s)"]
    assert results[0]["Title"] == "Sample Research Title"
    assert "sample abstract" in results[0]["Abstract"].lower()


# -------------------------------------
# Test search_and_fetch with mocks
# -------------------------------------
def test_search_and_fetch_success():
    # Mock search and fetch responses
    mock_search = MagicMock()
    mock_search.raise_for_status = lambda: None
    mock_search.json.return_value = {
        "esearchresult": {
            "idlist": ["12345678"]
        }
    }

    mock_fetch = MagicMock()
    mock_fetch.raise_for_status = lambda: None
    mock_fetch.text = SAMPLE_XML

    with patch("pubmed_fetcher.pubmed.requests.get", side_effect=[mock_search, mock_fetch]):
        results = pubmed.search_and_fetch("cancer treatment", retmax=1)
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]["PubmedID"] == "12345678"
        assert "Pfizer" in results[0]["CompanyAffiliation(s)"]
