from deep_translator import MyMemoryTranslator

from .translation_errors import InvalidLanguageError

SPANISH_LANGUAGE_NAMES = {
    "espanol": "es-ES",
    "ingles": "en-GB",
    "frances": "fr-FR",
    "aleman": "de-DE",
    "italiano": "it-IT",
    "portugues": "pt-PT",
    "catalan": "ca-ES",
    "euskera": "eu-ES",
    "gallego": "gl-ES",
    "neerlandes": "nl-NL",
    "ruso": "ru-RU",
    "chino": "zh-CN",
    "japones": "ja-JP",
    "coreano": "ko-KR",
    "arabe": "ar-SA",
}
SHORT_LANGUAGE_CODES = {
    "es": "es-ES",
    "en": "en-GB",
    "fr": "fr-FR",
    "de": "de-DE",
    "it": "it-IT",
    "pt": "pt-PT",
    "ca": "ca-ES",
    "eu": "eu-ES",
    "gl": "gl-ES",
    "nl": "nl-NL",
    "ru": "ru-RU",
    "zh": "zh-CN",
    "ja": "ja-JP",
    "ko": "ko-KR",
    "ar": "ar-SA",
}

ACCENTED_LETTERS = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u", "ñ": "n"}


def remove_accents(text):
    result = ""
    for letter in text:
        result += ACCENTED_LETTERS.get(letter, letter)
    return result


def normalize_language_input(text):
    if text is None:
        return ""
    return remove_accents(text.strip().lower())


def get_supported_languages():
    translator = MyMemoryTranslator(source="es-ES", target="en-GB")
    return translator.get_supported_languages(as_dict=True)


def find_language_code(user_input):
    text = normalize_language_input(user_input)

    if text in SPANISH_LANGUAGE_NAMES:
        return SPANISH_LANGUAGE_NAMES[text]

    if text in SHORT_LANGUAGE_CODES:
        return SHORT_LANGUAGE_CODES[text]

    for name, code in get_supported_languages().items():
        if text == normalize_language_input(name) or text == code.lower():
            return code

    return None


def is_valid_language(user_input):
    return find_language_code(user_input) is not None


def validate_language(user_input):
    code = find_language_code(user_input)
    if code is not None:
        return code

    text = normalize_language_input(user_input)
    if text == "":
        raise InvalidLanguageError(
            "No has escrito ningún idioma. Escríbelo de nuevo (por ejemplo: inglés o en-GB)."
        )

    has_numbers = False
    for letter in text:
        if letter.isdigit():
            has_numbers = True

    if has_numbers:
        raise InvalidLanguageError(
            f"El idioma '{user_input.strip()}' contiene números. "
            "Escríbelo de nuevo solo con letras (por ejemplo: francés)."
        )

    raise InvalidLanguageError(
        f"El idioma '{user_input.strip()}' no existe o está mal escrito. "
        "Revisa la ortografía y escríbelo de nuevo (por ejemplo: alemán o de-DE)."
    )


def ask_language(input_func=input, max_attempts=3):
    for _ in range(max_attempts):
        user_input = input_func("➤ Idioma de destino (ej. inglés, francés o en-GB): ")
        try:
            return validate_language(user_input)
        except InvalidLanguageError as error:
            print(f"⚠️  {error}")

    raise InvalidLanguageError(
        f"Has agotado los {max_attempts} intentos. Vuelve a empezar y escribe un idioma válido."
    )
