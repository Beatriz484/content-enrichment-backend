import logging

from src.logging_config import DEFAULT_LOG_FILE, setup_logging


def test_setup_logging_crea_el_archivo_de_log(tmp_path):
    log_file = tmp_path / "logs" / "app.log"
    logger = setup_logging(log_file=str(log_file))

    logger.info("Mensaje de prueba 12345")

    assert log_file.exists()
    contenido = log_file.read_text(encoding="utf-8")
    assert "Mensaje de prueba 12345" in contenido
    assert "[INFO]" in contenido
    assert _handlers_hacia(logger, log_file), "Debe existir un FileHandler configurado"


def test_setup_logging_es_idempotente(tmp_path):
    log_file = tmp_path / "app.log"

    setup_logging(log_file=str(log_file))
    logger = setup_logging(log_file=str(log_file))

    assert len(_handlers_hacia(logger, log_file)) == 1


def _handlers_hacia(logger: logging.Logger, log_file) -> list:
    destino = str(log_file.resolve())
    return [
        handler
        for handler in logger.handlers
        if isinstance(handler, logging.FileHandler)
        and handler.baseFilename == destino
    ]


def test_archivo_de_log_por_defecto():
    assert DEFAULT_LOG_FILE == "logs/app.log"
