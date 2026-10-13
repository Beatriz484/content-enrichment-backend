r"""Feature: Steps of the research pipeline

  As a Content Enricher user
  I want each step handed to the next one in a single agreed shape
  So that the pipeline can be stopped or continued without surprises
"""

from unittest.mock import patch

import pytest

from src.pipeline import _create_enricher, research_topic

RESEARCH_RESULT = {
    "title": "Python",
    "paragraphs": ["Párrafo uno.", "Párrafo dos."],
}
FULL_TEXT = "Párrafo uno.\n\nPárrafo dos."


def test_create_enricher_returns_none_without_credentials(monkeypatch, capsys):
    r"""@failure

    Scenario: Continue without AI when there are no credentials
        Given no OPENAI_API_KEY in the environment
        When the enricher is created
        Then no enricher is returned
        And the terminal says that AI is unavailable
    """
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert _create_enricher() is None
    assert "IA no disponible" in capsys.readouterr().out


def test_create_enricher_with_credentials(monkeypatch):
    r"""@successful

    Scenario: Create the enricher when credentials are present
        Given the environment variable OPENAI_API_KEY is "sk-test"
        When the enricher is created
        Then an enricher is returned
        And it holds the configured API key
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://ejemplo/v1")

    enricher = _create_enricher()

    assert enricher is not None
    assert enricher.api_key == "sk-test"


def test_research_topic_normalizes_scraper_output():
    r"""@successful

    Scenario: Normalise what the scraper returned into a single text
        Given a scraper that returns the title "Python" and two paragraphs
        When the topic "python" is researched
        Then I get the title "Python"
        And I get the same two paragraphs
        And I get the paragraphs joined into one text
    """
    with patch("src.pipeline.WikipediaScraper") as scraper_cls:
        scraper_cls.return_value.extract_content.return_value = dict(RESEARCH_RESULT)
        research = research_topic("python")

    assert research == {
        "title": "Python",
        "paragraphs": ["Párrafo uno.", "Párrafo dos."],
        "text": FULL_TEXT,
    }


def test_research_topic_propagates_scraper_errors():
    r"""@failure

    Scenario: Let the scraper failure reach the caller
        Given a scraper that raises the error "no existe"
        When the topic "tema inexistente" is researched
        Then the same error is raised
    """
    with patch("src.pipeline.WikipediaScraper", side_effect=ValueError("no existe")):
        with pytest.raises(ValueError, match="no existe"):
            research_topic("tema inexistente")
