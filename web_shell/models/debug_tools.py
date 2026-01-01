# -*- coding: utf-8 -*-
import logging
from odoo import models

_logger = logging.getLogger(__name__)


# Cache Inspection Tools
def get_cache_info(env, model_name, record_id):
    """
    Inspects the ORM cache for a specific record.
    """
    _logger.info(f"WebShell: Inspecting cache for {model_name}({record_id})")

    try:
        if model_name not in env:
            return {"error": f"Model {model_name} not found"}

        model = env[model_name]
        record = model.browse(int(record_id))

        if not record.exists():
            return {"error": f"Record {model_name}({record_id}) not found"}

        cache_data = []

        _logger.info(f"WebShell: Record found. Inspecting {len(model._fields)} fields.")

        # Iterate over fields to check cache
        # CHANGE: We read ALL fields to show current DB state, as inspecting "cache" of a fresh request is useless.
        for field_name, field in model._fields.items():
            try:
                # We check if it WAS in cache before accessing (just for info)
                is_cached = env.cache.contains(record, field)
                status = "cached" if is_cached else "fetched"

                # Read value (triggers fetch if not cached)
                val = getattr(record, field_name)

                # Format complex types
                relation_info = {}
                if isinstance(val, models.Model):
                    if val:
                        relation_info = {
                            "res_id": val.id,
                            "model": val._name,
                            "display_name": val.display_name or str(val),
                        }
                    val = f"{val._name}({val.id if val else ''})"

                res = {
                    "field": field_name,
                    "value": str(val),
                    "type": field.type,
                    "status": status,
                }
                if relation_info:
                    res["relation"] = relation_info

                cache_data.append(res)
            except Exception as e:
                # _logger.warning(f"WebShell: Error reading field {field_name}: {e}")
                cache_data.append(
                    {
                        "field": field_name,
                        "value": str(e),
                        "type": field.type,
                        "status": "error",
                    }
                )

        _logger.info(
            f"WebShell: Cache inspection done. Found {len(cache_data)} cached fields."
        )
        return {"fields": cache_data}

    except Exception as e:
        _logger.error(f"WebShell: Cache Inspection Fatal Error: {e}")
        return {"error": str(e)}


def get_view_inheritance(env, view_id):
    """Returns a recursive tree of views inheriting from the given view_id."""
    view = env["ir.ui.view"].browse(int(view_id))
    if not view.exists():
        return {}

    def get_children(v):
        # Search for views that inherit from v
        # We use [('inherit_id', '=', v.id)] to find direct children
        children = env["ir.ui.view"].search([("inherit_id", "=", v.id)])
        return {
            "id": v.id,
            "name": v.name,
            "xml_id": v.xml_id or f"__export__.{v.id}",
            "model": v.model,
            "arch_db": v.arch_db,
            "children": [get_children(child) for child in children],
        }

    return get_children(view)
