import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from SDK import setup_logger

logger = setup_logger(
    name="exemplo_app",
    username="test",
    password="test",
    level=logging.DEBUG
)
def test():
    logger.debug("Isto é uma mensagem de debug")
    logger.info("Aplicação iniciada")
    logger.warning("Aviso: recurso está quase esgotado")
    logger.error("Erro ao processar arquivo")

if __name__ == '__main__':
    test()
