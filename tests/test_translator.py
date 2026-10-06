"""Tests del stub de traducción (HU-04, pendiente de entrega por el equipo)."""
import pytest

from src.errors import ServicioNoDisponibleError
from src.translator import DeepTranslateTranslator


def test_el_stub_expone_el_contrato_acordado():
    """La pipeline espera exactamente este método, sin parámetros extra."""
    assert callable(DeepTranslateTranslator.translate)


def test_el_stub_avisa_en_lugar_de_devolver_una_cadena_vacia():
    """Nunca debe aparecer una sección de traducción vacía en el informe."""
    with pytest.raises(ServicioNoDisponibleError, match="DeepTranslate"):
        DeepTranslateTranslator().translate("texto original", "fr")
