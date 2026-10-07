"""Troceado de textos largos para respetar el límite de MyMemory.

MyMemory admite menos de 500 caracteres por petición. Usamos 400 como margen
de seguridad (la API habla de 500 bytes y las tildes y la ñ ocupan 2 bytes).
"""

# Máximo de caracteres por trozo
MAX_CHARS_PER_CHUNK = 400

# Signos que marcan el final de una frase
SENTENCE_ENDINGS = (".", "!", "?")


def split_sentences(text):
    """Separa el texto en frases. Una frase termina en '.', '!' o '?'."""
    sentences = []
    current_words = []
    for word in text.split():
        current_words.append(word)
        if word.endswith(SENTENCE_ENDINGS):
            sentences.append(" ".join(current_words))
            current_words = []

    # Lo que queda sin punto final también es una frase
    if current_words:
        sentences.append(" ".join(current_words))
    return sentences


def split_text(text, max_chars=MAX_CHARS_PER_CHUNK):
    """Divide el texto en trozos de como mucho ``max_chars`` sin cortar palabras.

    Junta frases enteras mientras quepan. Si una sola frase es más larga que
    el límite, la reparte por palabras.

    Returns:
        Lista de trozos en el mismo orden que el texto. Lista vacía si no hay texto.
    """
    chunks = []
    current = ""
    for sentence in split_sentences(text):
        # Una frase demasiado larga se reparte palabra a palabra
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
