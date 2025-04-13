import logging
import sys
import os

import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pyweblog.SDK_WS.main import setup_ws_logger

logger = setup_ws_logger(
    name="exemplo_app_ws",
    username="test@test.com",
    password="123",
    level=logging.DEBUG
)
if __name__ == '__main__':
    while True:
        logger.debug("Isto é uma mensagem de debug via WebSocket")
        logger.info("Aplicação iniciada via WebSocket")
        logger.warning("Aviso: recurso está quase esgotado (WebSocket)")
        logger.error("Erro ao processar arquivo (WebSocket)")


