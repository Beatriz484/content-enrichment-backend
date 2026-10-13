from unittest.mock import patch

import pytest

from src.pipeline import _create_enricher, research_topic

RESEARCH_RESULT = {
    "title": "Python",
    "paragraphs": ["Párrafo uno.", "Párrafo dos."],
}
FULL_TEXT = "Párrafo uno.\n\nPárrafo dos."


def test_create_enricher_returns_none_without_credentials(monkeypatch, capsys):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert _create_enricher() is None
    assert "IA no disponible" in capsys.readouterr().out


def test_create_enricher_with_credentials(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://ejemplo/v1")

    enricher = _create_enricher()

    assert enricher is not None
    assert enricher.api_key == "sk-test"


def test_research_topic_normalizes_scraper_output():
    with patch("src.pipeline.WikipediaScraper") as scraper_cls:
        scraper_cls.return_value.extract_content.return_value = dict(RESEARCH_RESULT)
        research = research_topic("python")

    assert research == {
        "title": "Python",
        "paragraphs": ["Párrafo uno.", "Párrafo dos."],
        "text": FULL_TEXT,
    }


def test_research_topic_propagates_scraper_errors():
    with patch("src.pipeline.WikipediaScraper", side_effect=ValueError("no existe")):
        with pytest.raises(ValueError, match="no existe"):
            research_topic("tema inexistente")
