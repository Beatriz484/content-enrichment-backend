from typing import Any, Dict, Optional, Tuple

VALID_FORMATS: Tuple[str, ...] = ("txt", "pdf")
AFFIRMATIVE_ANSWERS: Tuple[str, ...] = ("s", "si", "sí", "y", "yes")
NEGATIVE_ANSWERS: Tuple[str, ...] = ("n", "no")
RULE = "-" * 56


def ask_text(message: str) -> str:
    while True:
        answer = input(message).strip()
        if answer:
            return answer
        print("⚠️  El valor no puede estar vacío. Inténtalo de nuevo.")


def confirm(message: str, default: bool = True) -> bool:
    while True:
        answer = input(f"{message} (sí/no): ").strip().lower()
        if not answer:
            return default
        if answer in AFFIRMATIVE_ANSWERS:
            return True
        if answer in NEGATIVE_ANSWERS:
            return False
        print("⚠️  Responde 'sí' o 'no'.")


def ask_choice(message: str, options: Tuple[str, ...]) -> str:
    while True:
        answer = input(message).strip()
        if answer in options:
            return answer
        print(f"⚠️  Opción no válida. Por favor, introduce una de: {', '.join(options)}.")


def ask_translation_language() -> Optional[str]:
    answer = input("➤ Idioma de traducción (ej. en, fr — Enter = original): ").strip()
    return answer.lower() if answer else None


def ask_format() -> str:
    while True:
        output_format = input("➤ Formato del informe (txt / pdf): ").strip().lower()
        if output_format in VALID_FORMATS:
            return output_format
        print(f"⚠️  Formato no válido. Usa uno de: {', '.join(VALID_FORMATS)}.")


def show_investigation(research: Dict[str, Any]) -> None:
    print(f"\n=== TÍTULO: {research['title']} ===\n")
    for index, paragraph in enumerate(research["paragraphs"], 1):
        print(f"--- Párrafo {index} ---")
        print(f"{paragraph}\n")


def show_section(label: str, content: str) -> None:
    print(f"=== {label} ===")
    print(f"{content}\n")

