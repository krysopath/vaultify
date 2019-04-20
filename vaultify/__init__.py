import logging.config
from .config import configure

CFG = configure()
logging.config.dictConfig(CFG)
logger = logging.getLogger(__name__)
logger.debug("vaultify module initializing...")

from .vaultify import main

__all__ = "main" "CFG"
