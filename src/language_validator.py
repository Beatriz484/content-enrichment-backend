"""Validación del idioma de destino que escribe el usuario.

Acepta el nombre en español (solo los idiomas más comunes), el nombre en
inglés o el código que usa MyMemory (por ejemplo "en-GB"). No sugiere idiomas
parecidos: si hay un error, avisa y pide que se vuelva a escribir.
"""
from deep_translator import MyMemoryTranslator

from .translation_errors import InvalidLanguageError

# Nombres en español de los idiomas más comunes y su código en MyMemory.
# Se escriben sin tildes porque la entrada del usuario también se las quita.
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
# Códigos cortos (los que sugiere el menú del equipo) -> código que acepta MyMemory.
# Algunos son ambiguos (en, pt, zh, ar): se elige uno por defecto.
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

# Letras con tilde (y la ñ) y la letra sencilla que las sustituye
ACCENTED_LETTERS = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u", "ñ": "n"}


def remove_accents(text):
    """Cambia las letras con tilde por su versión sin tilde ("español" -> "espanol")."""
    result = ""
    for letter in text:
        result += ACCENTED_LETTERS.get(letter, letter)
    return result


def normalize_language_input(text):
    """Quita espacios a los lados, pasa a minúsculas y quita las tildes."""
    if text is None:
        return ""
    return remove_accents(text.strip().lower())


def get_supported_languages():
    """Devuelve el diccionario {nombre en inglés: código} que admite MyMemory."""
    translator = MyMemoryTranslator(source="es-ES", target="en-GB")
    return translator.get_supported_languages(as_dict=True)


def find_language_code(user_input):
    """Busca el código del idioma escrito. Devuelve None si no existe."""
    text = normalize_language_input(user_input)

    # 1. Nombre en español
    if text in SPANISH_LANGUAGE_NAMES:
        return SPANISH_LANGUAGE_NAMES[text]

    # 2. Código corto de dos letras (en, fr...) -> código largo de MyMemory
    if text in SHORT_LANGUAGE_CODES:
        return SHORT_LANGUAGE_CODES[text]

    # 3. Nombre en inglés o código de MyMemory (coincidencia exacta)
    for name, code in get_supported_languages().items():
        if text == normalize_language_input(name) or text == code.lower():
            return code

    return None


def is_valid_language(user_input):
    """True si el texto coincide exactamente con un idioma soportado."""
    return find_language_code(user_input) is not None


def validate_language(user_input):
    """Devuelve el código del idioma o lanza InvalidLanguageError con el motivo."""
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
    """Pide el idioma de destino hasta que sea válido y devuelve su código.

    Args:
        input_func: Función que lee lo que escribe el usuario. Por defecto
            ``input``; en los tests se cambia por una entrada simulada.
        max_attempts: Número máximo de intentos.

    Raises:
        InvalidLanguageError: si se agotan los intentos.
    """
    for _ in range(max_attempts):
        user_input = input_func("➤ Idioma de destino (ej. inglés, francés o en-GB): ")
        try:
            return validate_language(user_input)
        except InvalidLanguageError as error:
            print(f"⚠️  {error}")

    raise InvalidLanguageError(
        f"Has agotado los {max_attempts} intentos. Vuelve a empezar y escribe un idioma válido."
    )
