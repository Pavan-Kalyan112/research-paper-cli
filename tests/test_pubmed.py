import pytest
from unittest.mock import patch, MagicMock
from pubmed_fetcher.pubmed import search_and_fetch, parse_pubmed_xml

FAKE_XML_RESPONSE = """
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <Article>
        <ArticleTitle>New Insights into Cancer Treatment</ArticleTitle>
        <Abstract>
          <AbstractText>Innovative approaches in cancer therapy are discussed.</AbstractText>
        </Abstract>
        <AuthorList>
          <Author>
            <LastName>Doe</LastName>
            <ForeName>Jane</ForeName>
            <AffiliationInfo>
              <Affiliation>Pfizer Inc., Oncology Division, USA. Email: jane.doe@pfizer.com</Affiliation>
            </AffiliationInfo>
          </Author>
        </AuthorList>
      </Article>
      <DateCompleted>
        <Year>2023</Year>
      </DateCompleted>
    </MedlineCitation>
  </PubmedArticle>
</PubmedArticleSet>
"""

def test_parse_pubmed_xml_fields():
    ids = ["987654"]
    results = parse_pubmed_xml(FAKE_XML_RESPONSE, ids)
    assert len(results) == 1

    paper = results[0]

    assert paper["PubmedID"] == "987654"
    assert paper["Title"] == "New Insights into Cancer Treatment"
    assert paper["Publication Date"] == "2023"
    assert "Pfizer" in paper["CompanyAffiliation(s)"]
    assert "jane.doe@pfizer.com" in paper["Corresponding Author Email"]
    assert paper["Non-academicAuthor(s)"]  # Should not be empty

@patch("pubmed_fetcher.pubmed.requests.get")
def test_search_and_fetch_pipeline(mock_get):
    # Mock the ESearch API
    mock_search = MagicMock()
    mock_search.json.return_value = {"esearchresult": {"idlist": ["987654"]}}
    mock_search.raise_for_status = lambda: None

    # Mock the EFetch API
    mock_fetch = MagicMock()
    mock_fetch.text = FAKE_XML_RESPONSE
    mock_fetch.raise_for_status = lambda: None

    mock_get.side_effect = [mock_search, mock_fetch]

    results = search_and_fetch("cancer therapy", retmax=1)
    assert len(results) == 1

    paper = results[0]
    assert "PubmedID" in paper
    assert "Title" in paper
    assert "Publication Date" in paper
    assert "Non-academicAuthor(s)" in paper
    assert "CompanyAffiliation(s)" in paper
    assert "Corresponding Author Email" in paper
