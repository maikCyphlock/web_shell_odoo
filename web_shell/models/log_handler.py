# -*- coding: utf-8 -*-
# Part of Web Shell. See LICENSE file for full copyright and licensing details.
# Created by MAIKOL AGUILAR (https://github.com/maikol-aguilar)

import logging
import odoo
from odoo.http import request

_logger = logging.getLogger(__name__)

class BusLogHandler(logging.Handler):
    def emit(self, record):
        try:
            # We use the request environment to push to the bus.
            # This requires an active request context.
            # Accessing request.env will raise RuntimeError if unbound.
            if not request:
                return

            env = request.env
            
            # Format message (this populates record.asctime)
            msg = self.format(record)
            
            # Send to bus
            env['bus.bus']._sendone('web_shell_logs', 'log_message', {
                'level': record.levelname,
                'name': record.name,
                'message': msg,
                'time': getattr(record, 'asctime', str(record.created))
            })
        except (RuntimeError, AttributeError, KeyError):
            # Context unavailable
            pass
        except Exception as e:
            # Safe fallback print for real errors
            print(f"WebShell Log Error: {e}")

# Register the handler
# Register the handler
def register_log_handler():
    print("DEBUG: Registering Web Shell BusLogHandler...")
    handler = BusLogHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Add to root logger
    logging.getLogger().addHandler(handler)
    
    # Add to specific loggers to ensure we catch them
    logging.getLogger('odoo').addHandler(handler)
    logging.getLogger('werkzeug').addHandler(handler)
    
    print("DEBUG: Web Shell BusLogHandler registered on root, odoo, and werkzeug.")

# We can call this from __init__ or use a proper Odoo hook. 
# Identifying a clean place to register it once is key.
# For now, we'll instantiate it at the global scope of this file, 
# but guarded to only add if not present?
# Logging handlers can duplicate if we are not careful with reloads.
# A safer bet is to add it in the register_hook of the main model or in __init__.
