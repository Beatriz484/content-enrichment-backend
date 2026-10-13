from unittest.mock import patch

import pytest

from src.prompts import ask_choice, ask_format, ask_text, confirm


def test_ask_text_retries_until_non_empty(capsys):
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
    with patch("builtins.input", side_effect=[answer]):
        assert confirm("¿Guardar?", True) is expected


def test_confirm_retries_on_invalid_answer(capsys):
    with patch("builtins.input", side_effect=["tal vez", "sí"]):
        assert confirm("¿Guardar?", False) is True

    assert "Responde 'sí' o 'no'" in capsys.readouterr().out


def test_ask_format_retries_until_valid(capsys):
    with patch("builtins.input", side_effect=["docx", "TXT"]):
        assert ask_format() == "txt"

    assert "Formato no válido" in capsys.readouterr().out


def test_ask_choice_retries_until_valid_option(capsys):
    with patch("builtins.input", side_effect=["3", "2"]):
        assert ask_choice("➤ Elige una opción (1 / 2): ", ("1", "2")) == "2"

    assert "Opción no válida" in capsys.readouterr().out
