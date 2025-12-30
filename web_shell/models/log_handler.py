# -*- coding: utf-8 -*-
# Part of Web Shell. See LICENSE file for full copyright and licensing details.
# Created by MAIKOL AGUILAR (https://github.com/maikCyphlock)

import logging
from odoo.http import request

_logger = logging.getLogger(__name__)


class BusLogHandler(logging.Handler):
    def emit(self, record):
        try:
            # We use the request environment to push to the bus.
            # This requires an active request context.
            # Accessing request.env will raise RuntimeError if unbound.
            if not request or not getattr(request, "env", None):
                return

            env = request.env

            # Format message (this populates record.asctime)
            msg = self.format(record)

            # Send to bus
            # Use user's partner channel which is always allowed (if user is logged in)
            if not request.env.user or not request.env.user.partner_id:
                return

            channel = request.env.user.partner_id
            env["bus.bus"]._sendone(
                channel,
                "web_shell_log",
                {
                    "level": record.levelname,
                    "name": record.name,
                    "message": msg,
                    "time": getattr(record, "asctime", str(record.created)),
                },
            )
        except (RuntimeError, AttributeError, KeyError, TypeError):
            # Context unavailable
            pass
        except Exception:
            # CRUDELY IGNORE ALL ERRORS.
            # If the cursor is closed, or anything else goes wrong during logging,
            # we simply want to silence it to prevent the server from crashing.
            pass


# Register the handler
# Register the handler
def register_log_handler():
    print("DEBUG: Registering Web Shell BusLogHandler...")
    handler = BusLogHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Add to root logger
    logging.getLogger().addHandler(handler)

    # Add to specific loggers to ensure we catch them
    logging.getLogger("odoo").addHandler(handler)
    logging.getLogger("werkzeug").addHandler(handler)

    print("DEBUG: Web Shell BusLogHandler registered on root, odoo, and werkzeug.")


# We can call this from __init__ or use a proper Odoo hook.
# Identifying a clean place to register it once is key.
# For now, we'll instantiate it at the global scope of this file,
# but guarded to only add if not present?
# Logging handlers can duplicate if we are not careful with reloads.
# A safer bet is to add it in the register_hook of the main model or in __init__.
