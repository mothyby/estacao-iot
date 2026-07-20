import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from coleta.config import LOG_FILE

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("EstacaoIoT")
    
    # 1. Evita duplicação de handlers se o módulo for reimportado
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. RotatingFileHandler (Max 5MB por arquivo, até 5 backups = 25MB máx)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()
