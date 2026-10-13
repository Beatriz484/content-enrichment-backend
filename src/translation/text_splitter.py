MAX_CHARS_PER_CHUNK = 400

SENTENCE_ENDINGS = (".", "!", "?")


def split_sentences(text):
    sentences = []
    current_words = []
    for word in text.split():
        current_words.append(word)
        if word.endswith(SENTENCE_ENDINGS):
            sentences.append(" ".join(current_words))
            current_words = []

    if current_words:
        sentences.append(" ".join(current_words))
    return sentences


def split_text(text, max_chars=MAX_CHARS_PER_CHUNK):
    chunks = []
    current = ""
    for sentence in split_sentences(text):
        if len(sentence) <= max_chars:
            pieces = [sentence]
        else:
            pieces = sentence.split(" ")

        for piece in pieces:
            if current == "":
                current = piece
            elif len(current) + 1 + len(piece) <= max_chars:
                current = current + " " + piece
            else:
                chunks.append(current)
                current = piece

    if current:
        chunks.append(current)
    return chunks
