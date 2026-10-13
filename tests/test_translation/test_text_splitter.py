from src.translation.text_splitter import split_text

SENTENCE = "La investigación científica avanza rápidamente cada año."


def test_split_a_short_text():
    r"""@successful

    Scenario: Keep a short text in a single chunk
        Given the text "Hola. ¿Qué tal?"
        When I split it into chunks of 400 characters
        Then I get 1 chunk equal to the text
    """
    text = "Hola. ¿Qué tal?"

    chunks = split_text(text, 400)

    assert chunks == [text]


def test_split_a_long_text_by_sentences():
    r"""@successful

    Scenario: Split a long text on sentence boundaries
        Given a text of 20 identical sentences
        When I split it into chunks of 400 characters
        Then I get more than 1 chunk
        And every chunk is at most 400 characters long
        And every chunk ends with a sentence
        And joining the chunks gives the original text back
    """
    text = " ".join([SENTENCE] * 20)

    chunks = split_text(text, 400)

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 400
        assert chunk.endswith(".")
    assert " ".join(chunks) == text


def test_split_a_single_sentence_longer_than_the_limit():
    r"""@successful

    Scenario: Split a single sentence that is longer than the limit
        Given a sentence of 120 words with no full stops in between
        When I split it into chunks of 400 characters
        Then I get more than 1 chunk
        And every chunk is at most 400 characters long
        And no word is cut in half
        And joining the chunks gives the original text back
    """
    text = " ".join(["palabra"] * 120) + "."

    chunks = split_text(text, 400)

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 400
        for word in chunk.split():
            assert word in ("palabra", "palabra.")
    assert " ".join(chunks) == text


def test_split_an_empty_text():
    r"""@failure

    Scenario: Produce no chunks at all for an empty text
        Given the text ""
        When I split it into chunks of 400 characters
        Then I get an empty list
    """
    assert split_text("", 400) == []
