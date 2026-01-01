from . import console
from . import log_handler
from . import debug_tools

# Register the log handler once
import logging

handler_name = "WebShellBusHandler"
logger = logging.getLogger()
if not any(h.name == handler_name for h in logger.handlers):
    h = log_handler.BusLogHandler()
    h.name = handler_name
    h.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(h)
