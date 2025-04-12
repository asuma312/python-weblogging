import logging
import sys
import os

import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from SDK import setup_ws_logger

logger = setup_ws_logger(
    name="exemplo_app_ws",
    username="test",
    password="test",
    level=logging.DEBUG
)
while True:
    logger.debug("Isto é uma mensagem de debug via WebSocket")
    time.sleep(1)
    logger.info("Aplicação iniciada via WebSocket")
    time.sleep(1)
    logger.warning("Aviso: recurso está quase esgotado (WebSocket)")
    time.sleep(1)
    logger.error("Erro ao processar arquivo (WebSocket)")
    time.sleep(1)


