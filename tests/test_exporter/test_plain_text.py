import pytest

from src.exporter.plain_text import markdown_to_plain_text


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("## Granada", "Granada"),
        ("### 1. Geografía", "1. Geografía"),
        ("La **Vega de Granada** es fértil", "La Vega de Granada es fértil"),
        ("Se sitúa en __Andalucía__", "Se sitúa en Andalucía"),
        ("Una *gran* ciudad", "Una gran ciudad"),
        ("> **Dato técnico:** nieblas", "Dato técnico: nieblas"),
        ("Usa `python` para esto", "Usa python para esto"),
        ("Ver [Granada](https://granada.es) hoy", "Ver Granada (https://granada.es) hoy"),
        ("Superficie: 88 km² [[1]](#ref1)", "Superficie: 88 km² [1]"),
    ],
)
def test_markdown_symbols_are_removed_from_a_line(line, expected):
    r"""@successful

    Scenario Outline: Remove the Markdown symbols from a line
        Given a line written in Markdown <line>
        When I convert it to plain text
        Then the line is <expected>

        Examples:
            | line                                    | expected                               |
            | "## Granada"                            | "Granada"                              |
            | "### 1. Geografía"                      | "1. Geografía"                         |
            | "La **Vega de Granada** es fértil"      | "La Vega de Granada es fértil"         |
            | "Se sitúa en __Andalucía__"             | "Se sitúa en Andalucía"                |
            | "Una *gran* ciudad"                     | "Una gran ciudad"                      |
            | "> **Dato técnico:** nieblas"           | "Dato técnico: nieblas"                |
            | "Usa `python` para esto"                | "Usa python para esto"                 |
            | "Ver [Granada](https://granada.es) hoy" | "Ver Granada (https://granada.es) hoy" |
            | "Superficie: 88 km² [[1]](#ref1)"       | "Superficie: 88 km² [1]"               |
    """
    assert markdown_to_plain_text(line) == expected


def test_horizontal_rule_becomes_a_blank_line():
    r"""@successful

    Scenario: Replace a horizontal rule with a blank line
        Given a text with a "---" line between "Uno" and "Dos"
        When I convert it to plain text
        Then "Uno" and "Dos" are separated by one blank line
    """
    assert markdown_to_plain_text("Uno\n---\nDos") == "Uno\n\nDos"


def test_tables_become_one_row_per_line():
    r"""@successful

    Scenario: Turn a table into one row per line
        Given a table with the header "Elemento" and "Descripción" and the row "Altitud" and "680 m"
        When I convert it to plain text
        Then each row is written on its own line with " - " between the cells
        And the line of dashes is removed
    """
    table = (
        "| Elemento | Descripción |\n"
        "|----------|-------------|\n"
        "| **Altitud** | 680 m |"
    )
    assert markdown_to_plain_text(table) == "Elemento - Descripción\nAltitud - 680 m"


def test_dash_lists_are_kept():
    r"""@successful

    Scenario: Keep the lists written with dashes
        Given a list with "- **Población:** 235 294" and "- Barrios: 7"
        When I convert it to plain text
        Then the list keeps its dashes without the bold symbols
    """
    text = "- **Población:** 235 294\n- Barrios: 7"
    assert markdown_to_plain_text(text) == "- Población: 235 294\n- Barrios: 7"


def test_asterisk_lists_become_dash_lists():
    r"""@successful

    Scenario: Change the lists written with asterisks into dash lists
        Given a list with "* uno" and "* dos"
        When I convert it to plain text
        Then the list is "- uno" and "- dos"
    """
    assert markdown_to_plain_text("* uno\n* dos") == "- uno\n- dos"


def test_text_without_markdown_is_not_changed():
    r"""@successful

    Scenario: Leave a text without Markdown as it is
        Given a text with two paragraphs and no Markdown symbols
        When I convert it to plain text
        Then the text is exactly the same
    """
    text = "Párrafo uno.\n\nPárrafo dos."
    assert markdown_to_plain_text(text) == text


def test_consecutive_blank_lines_are_collapsed_into_one():
    r"""@successful

    Scenario: Collapse several blank lines into one
        Given a text with four blank lines between "Uno" and "Dos"
        When I convert it to plain text
        Then "Uno" and "Dos" are separated by only one blank line
    """
    assert markdown_to_plain_text("Uno\n\n\n\nDos") == "Uno\n\nDos"
