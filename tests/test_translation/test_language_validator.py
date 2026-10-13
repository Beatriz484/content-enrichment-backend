r"""Feature: Validation of the target language typed by the user

  As a Content Enricher user
  I want my language rejected with a clear message when it is wrong
  So that the pipeline never asks MyMemory for a language it does not understand
"""

import pytest

from src.translation.language_validator import (
    ask_language,
    is_valid_language,
    validate_language,
)
from src.translation.translation_errors import InvalidLanguageError


def scripted_input(answers):
    pending = list(answers)

    def read(prompt):
        return pending.pop(0)

    return read


@pytest.mark.parametrize(
    "entry, code",
    [
        ("español", "es-ES"),
        ("espanol", "es-ES"),
        ("  INGLÉS  ", "en-GB"),
        ("french", "fr-FR"),
        ("de-DE", "de-DE"),
    ],
    ids=[
        "spanish_name",
        "spanish_name_without_accent",
        "uppercase_and_spaces",
        "english_name",
        "mymemory_code",
    ],
)
def test_write_a_valid_language(entry, code):
    r"""@successful

    Scenario Outline: Accept the language written in any accepted spelling
        When I write the language <entry>
        Then the language is considered valid
        And I get the code "<code>"

        Examples:
            | entry        | code  |
            | "español"    | es-ES |
            | "espanol"    | es-ES |
            | "  INGLÉS  " | en-GB |
            | "french"     | fr-FR |
            | "de-DE"      | de-DE |
    """
    assert is_valid_language(entry) is True
    assert validate_language(entry) == code


@pytest.mark.parametrize(
    "entry, message",
    [
        ("espanil", "no existe o está mal escrito"),
        ("3spañol", "contiene números"),
        ("123", "contiene números"),
        ("", "No has escrito ningún idioma"),
        ("mesa", "no existe o está mal escrito"),
    ],
    ids=[
        "one_typo",
        "digit_sneaked_in",
        "only_digits",
        "empty",
        "text_that_is_not_a_language",
    ],
)
def test_write_a_language_with_errors(entry, message):
    r"""@failure

    Scenario Outline: Reject a language that cannot be understood
        When I write the language <entry>
        Then the language is considered invalid
        And the error message says "<message>"

        Examples:
            | entry      | message                      |
            | "espanil"  | no existe o está mal escrito |
            | "3spañol"  | contiene números             |
            | "123"      | contiene números             |
            | ""         | No has escrito ningún idioma |
            | "mesa"     | no existe o está mal escrito |
    """
    assert is_valid_language(entry) is False
    with pytest.raises(InvalidLanguageError, match=message):
        validate_language(entry)


def test_receive_an_empty_language_from_the_form():
    r"""@failure

    Scenario: Reject an empty language sent by the form
        Given the form answers nothing because Enter was pressed
        When the language is validated
        Then the language is considered invalid
        And the error message says "No has escrito ningún idioma"
    """
    with pytest.raises(InvalidLanguageError, match="No has escrito ningún idioma"):
        validate_language(None)


def test_one_failed_attempt_and_then_a_correct_one(capsys):
    r"""@successful

    Scenario: Accept the language on the second attempt
        Given the user writes "espanil" and then "francés"
        When the language is requested
        Then a warning says "no existe o está mal escrito"
        And the chosen language is "fr-FR"
    """
    code = ask_language(input_func=scripted_input(["espanil", "francés"]))

    assert "no existe o está mal escrito" in capsys.readouterr().out
    assert code == "fr-FR"


def test_exhaust_the_attempts():
    r"""@failure

    Scenario: Give up once every attempt has been used
        Given the user writes "3spañol", "123" and ""
        When the language is requested with 3 attempts
        Then the error message says that the 3 attempts are used up
    """
    with pytest.raises(InvalidLanguageError, match="Has agotado los 3 intentos"):
        ask_language(input_func=scripted_input(["3spañol", "123", ""]), max_attempts=3)


@pytest.mark.parametrize(
    "entry, expected",
    [
        ("en", "en-GB"),
        ("fr", "fr-FR"),
        ("EN ", "en-GB"),
        ("Fr", "fr-FR"),
        ("pt", "pt-PT"),
    ],
)
def test_a_short_code_converts_to_the_mymemory_code(entry, expected):
    r"""@successful

    Scenario Outline: Convert a short language code into the MyMemory code
        When I write the language <entry>
        Then I get the code "<expected>"

        Examples:
            | entry   | expected |
            | "en"    | en-GB    |
            | "fr"    | fr-FR    |
            | "EN "   | en-GB    |
            | "Fr"    | fr-FR    |
            | "pt"    | pt-PT    |
    """
    assert validate_language(entry) == expected


def test_an_unknown_short_code_raises():
    r"""@failure

    Scenario: Reject a short language code that does not exist
        When I write the language "xx"
        Then the language is considered invalid
        And an invalid language error is raised
    """
    with pytest.raises(InvalidLanguageError):
        validate_language("xx")
