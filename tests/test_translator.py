"""Tests del stub de traducción (HU-04, pendiente de entrega por el equipo)."""
import pytest

from src.errors import ServiceUnavailableError, ServicioNoDisponibleError
from src.translator import DeepTranslateTranslator


def test_stub_exposes_the_agreed_contract():
    """La CLI espera exactamente este método, sin parámetros extra."""
    assert callable(DeepTranslateTranslator.translate)


def test_stub_warns_instead_of_returning_empty_text():
    """Nunca debe aparecer una sección de traducción vacía en el informe."""
    with pytest.raises(ServiceUnavailableError, match="DeepTranslate"):
        DeepTranslateTranslator().translate("texto original", "fr")


def test_spanish_error_name_is_kept_for_the_teammate_module():
    """Compatibility: src/translator.py importa el error por su nombre en español."""
    assert ServicioNoDisponibleError is ServiceUnavailableError
