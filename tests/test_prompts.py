r"""Feature: Dialogue between the CLI and the user

  As a Content Enricher user
  I want every question repeated until I give an answer the system understands
  So that a typo never ends the run
"""

from unittest.mock import patch

import pytest

from src.prompts import ask_choice, ask_format, ask_text, confirm


def test_ask_text_retries_until_non_empty(capsys):
    r"""@successful

    Scenario: Ask again until a non empty topic is given
        Given the user types "", then "  ", then "python"
        When the topic is requested
        Then the topic is "python"
        And the terminal warns that the topic cannot be empty
    """
    with patch("builtins.input", side_effect=["", "  ", "python"]):
        assert ask_text("Tema: ") == "python"

    assert "no puede estar vacío" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        ("", True),
        ("si", True),
        ("no", False),
        ("N", False),
    ],
)
def test_confirm_answers(answer, expected):
    r"""@successful

    Scenario Outline: Read a yes or no answer
        Given the default answer is yes
        When I answer <answer> to the question
        Then the confirmation is <expected>

        Examples:
            | answer | expected |
            | ""     | true     |
            | "si"   | true     |
            | "no"   | false    |
            | "N"    | false    |
    """
    with patch("builtins.input", side_effect=[answer]):
        assert confirm("¿Guardar?", True) is expected


def test_confirm_retries_on_invalid_answer(capsys):
    r"""@successful

    Scenario: Ask again when the answer is neither yes nor no
        Given the user types "tal vez", then "sí"
        When the confirmation is requested with the default no
        Then the confirmation is true
        And the terminal explains that the answer must be "sí" or "no"
    """
    with patch("builtins.input", side_effect=["tal vez", "sí"]):
        assert confirm("¿Guardar?", False) is True

    assert "Responde 'sí' o 'no'" in capsys.readouterr().out


def test_ask_format_retries_until_valid(capsys):
    r"""@successful

    Scenario: Ask again when the export format is not supported
        Given the user types "docx", then "TXT"
        When the export format is requested
        Then the format is "txt"
        And the terminal warns that the format is not valid
    """
    with patch("builtins.input", side_effect=["docx", "TXT"]):
        assert ask_format() == "txt"

    assert "Formato no válido" in capsys.readouterr().out


def test_ask_choice_retries_until_valid_option(capsys):
    r"""@successful

    Scenario: Ask again when the chosen option is out of range
        Given the user types "3", then "2"
        When a choice is requested between the options "1" and "2"
        Then the chosen option is "2"
        And the terminal warns that the option is not valid
    """
    with patch("builtins.input", side_effect=["3", "2"]):
        assert ask_choice("➤ Elige una opción (1 / 2): ", ("1", "2")) == "2"

    assert "Opción no válida" in capsys.readouterr().out
