import pytest
from unittest.mock import patch, Mock
from pubmed_fetcher.data_pipeline import (
    fetch_pubmed_ids,
    fetch_articles_xml,
    extract_info,
    search_and_fetch
)
import xml.etree.ElementTree as ET

# Sample mock response for ESearch
mock_esearch_response = {
    "esearchresult": {
        "idlist": ["12345678", "23456789"]
    }
}

# Sample mock XML for EFetch
mock_efetch_xml = """
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>12345678</PMID>
      <Article>
        <ArticleTitle>Sample Research on Vaccine</ArticleTitle>
        <Abstract>
          <AbstractText>This is a test abstract about vaccine efficacy.</AbstractText>
        </Abstract>
        <AuthorList>
          <Author>
            <LastName>Doe</LastName>
            <ForeName>John</ForeName>
            <AffiliationInfo>
              <Affiliation>Moderna Inc, Research Department, john.doe@moderna.com</Affiliation>
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

@patch("pubmed_fetcher.data_pipeline.requests.get")
def test_fetch_pubmed_ids(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = mock_esearch_response
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    ids = fetch_pubmed_ids("vaccine", max_results=2)
    assert ids == ["12345678", "23456789"]

@patch("pubmed_fetcher.data_pipeline.requests.get")
def test_fetch_articles_xml(mock_get):
    mock_response = Mock()
    mock_response.content = mock_efetch_xml.encode("utf-8")
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    xml_root = fetch_articles_xml(["12345678"])
    assert isinstance(xml_root, ET.Element)
    assert xml_root.findtext(".//PMID") == "12345678"

def test_extract_info_parsing():
    root = ET.fromstring(mock_efetch_xml)
    article = root.find(".//PubmedArticle")
    paper = extract_info(article)

    assert paper["PubmedID"] == "12345678"
    assert paper["Title"] == "Sample Research on Vaccine"
    assert "John Doe" in paper["Authors"]
    assert "Moderna" in paper["CompanyAffiliation(s)"]
    assert "john.doe@moderna.com" in paper["Corresponding Author Email"]
    assert "This is a test abstract" in paper["Abstract"]

@patch("pubmed_fetcher.data_pipeline.fetch_pubmed_ids")
@patch("pubmed_fetcher.data_pipeline.fetch_articles_xml")
def test_search_and_fetch(mock_fetch_xml, mock_fetch_ids):
    mock_fetch_ids.return_value = ["12345678"]
    mock_fetch_xml.return_value = ET.fromstring(mock_efetch_xml)

    results = search_and_fetch("vaccine", limit=1)
    assert len(results) == 1
    assert results[0]["PubmedID"] == "12345678"
    assert "Moderna" in results[0]["CompanyAffiliation(s)"]
