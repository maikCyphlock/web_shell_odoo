# -*- coding: utf-8 -*-
# Part of Web Shell. See LICENSE file for full copyright and licensing details.
# Created by MAIKOL AGUILAR (https://github.com/maikCyphlock)

import sys
import io
import traceback
import logging
import difflib
from lxml import etree

from odoo import models, api, fields
from odoo.tools.profiler import Profiler
import time
import contextlib
from .debug_tools import get_cache_info

_logger = logging.getLogger(__name__)

# Global session storage: {user_id: user_variables_dict}
# Warning: This is memory-only and per-worker. Multi-worker setups will have inconsistent state.
# We ONLY store user-defined variables here, NOT env or self (which are request-specific)
SESSION_LOCALS = {}


class WebShellConsole(models.Model):
    _name = "web.shell.console"
    _description = "Web Shell Console"

    # Default blocked patterns - can be overridden via ir.config_parameter
    DEFAULT_BLOCKED_PATTERNS = [
        "os.system",
        "os.popen",
        "subprocess",
        "shutil.rmtree",
        "__import__",
    ]

    def _get_blocked_patterns(self):
        """Get blocked patterns from config or use defaults."""
        ICP = self.env["ir.config_parameter"].sudo()
        patterns_str = ICP.get_param("web_shell.blocked_patterns", "")
        if patterns_str:
            return [p.strip() for p in patterns_str.split(",") if p.strip()]
        return self.DEFAULT_BLOCKED_PATTERNS

    def _get_timeout(self):
        """Get execution timeout from config (default 30 seconds)."""
        ICP = self.env["ir.config_parameter"].sudo()
        try:
            return int(ICP.get_param("web_shell.timeout", "30"))
        except ValueError:
            return 30

    def _check_blocked_patterns(self, code):
        """Check if code contains any blocked patterns."""
        patterns = self._get_blocked_patterns()
        for pattern in patterns:
            if pattern in code:
                raise Exception(
                    f"Comando bloqueado: '{pattern}' no está permitido. "
                    f"Configurable via ir.config_parameter 'web_shell.blocked_patterns'"
                )

    @api.model
    def execute_command(self, code, safe_mode=False):
        """
        Executes python code and returns the output.
        Security features:
        - Audit logging of all commands
        - Configurable timeout (web_shell.timeout, default 30s)
        - Configurable blocked patterns (web_shell.blocked_patterns)
        - Safe Mode: automatic rollback of database changes
        """
        import signal

        if not self.env.user.has_group("base.group_system"):
            raise Exception(
                "Access Denied: You must be a system administrator to use the shell."
            )

        user_id = self.env.user.id
        user_login = self.env.user.login

        # SECURITY: Audit logging
        _logger.warning(
            "WEB_SHELL AUDIT - User: %s (ID: %d) executing (SafeMode=%s): %s",
            user_login,
            user_id,
            safe_mode,
            code[:500],
        )

        # SECURITY: Check for blocked patterns
        self._check_blocked_patterns(code)

        # Initialize user session if needed (only user variables, no env/self!)
        if user_id not in SESSION_LOCALS:
            SESSION_LOCALS[user_id] = {}

        # Create execution context with FRESH env and self for THIS request
        # Merge with user's persistent variables
        execution_context = {
            "env": self.env,
            "self": self,
            "models": models,
            "fields": fields,
            "api": api,
            **SESSION_LOCALS[user_id],  # User variables overlay
        }

        # Capture stdout/stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        original_stdout = sys.stdout
        original_stderr = sys.stderr

        sys.stdout = stdout_capture
        sys.stderr = stderr_capture

        # SECURITY: Timeout handler
        timeout = self._get_timeout()

        def timeout_handler(signum, frame):
            raise TimeoutError(
                f"Ejecución excedió el tiempo límite ({timeout}s). "
                f"Configurable via ir.config_parameter 'web_shell.timeout'"
            )

        class SafeModeRollback(Exception):
            pass

        result = None
        timeout_enabled = False
        try:
            # Set timeout (only works on Unix)
            # Signal only works in main thread
            if hasattr(signal, "SIGALRM"):
                try:
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(timeout)
                    timeout_enabled = True
                except ValueError:
                    # Occurs if we are not in the main thread
                    _logger.warning("WebShell: Cannot use timeout in non-main thread")

            try:

                def _run_code():
                    # Try to eval first (for expressions), then exec (for statements)
                    try:
                        # Compile as 'eval' to see if it's an expression
                        # This allows typing "1+1" and getting "2" without "print"
                        compiled = compile(code, "<string>", "eval")
                        result_obj = eval(compiled, execution_context)
                        if result_obj is not None:
                            print(repr(result_obj))
                    except SyntaxError:
                        # If it's not an expression, exec it
                        exec(code, execution_context)

                if safe_mode:
                    try:
                        with self.env.cr.savepoint():
                            try:
                                _run_code()
                                raise SafeModeRollback()
                            finally:
                                pass
                    except SafeModeRollback:
                        print("\n SAFE MODE: Transaction rolled back automatically.")
                else:
                    _run_code()

            except TimeoutError:
                raise
            except Exception:
                traceback.print_exc()
        finally:
            # Cancel timeout
            if hasattr(signal, "SIGALRM") and timeout_enabled:
                signal.alarm(0)
            sys.stdout = original_stdout
            sys.stderr = original_stderr

        # Save back user-defined variables (exclude env, self, builtins, modules)
        # This preserves user variables across commands
        for key, value in execution_context.items():
            if key not in ("env", "self", "models", "fields", "api", "__builtins__"):
                SESSION_LOCALS[user_id][key] = value

        output = stdout_capture.getvalue() + stderr_capture.getvalue()
        return output

    @api.model
    def test_log(self):
        """Generates test logs at different levels"""
        logger = logging.getLogger("odoo.addons.web_shell")
        logger.info("Test INFO log from Web Shell")
        logger.warning("Test WARNING log from Web Shell")
        return True

    @api.model
    def read_logs(self, last_position=0, max_lines=100):
        """
        Reads logs directly from the Odoo log file.
        Returns: { 'lines': [...], 'position': new_pos, 'error': ... }
        """
        if not self.env.user.has_group("base.group_system"):
            raise Exception("Access Denied")

        import os

        LOG_FILE_PATHS = [
            "/var/log/odoo/odoo-server.log",
            "/var/log/odoo/odoo.log",
            "/proc/1/fd/1",
        ]

        log_file = None
        for path in LOG_FILE_PATHS:
            if os.path.exists(path) and os.access(path, os.R_OK):
                log_file = path
                break

        if not log_file:
            # Fallback if no log file found (dev environment)
            return {"lines": [], "position": 0, "error": "Log file not found"}

        try:
            with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                f.seek(0, 2)
                file_size = f.tell()

                if last_position == 0:
                    read_size = min(50000, file_size)
                    f.seek(max(0, file_size - read_size))
                    content = f.read()
                    lines = content.strip().split("\n")[-max_lines:]
                    new_position = file_size
                elif last_position < file_size:
                    f.seek(last_position)
                    content = f.read()
                    lines = content.strip().split("\n") if content.strip() else []
                    lines = lines[-max_lines:] if len(lines) > max_lines else lines
                    new_position = file_size
                else:
                    lines = []
                    new_position = file_size

                parsed_lines = []
                for line in lines:
                    if line.strip():
                        parsed_lines.append(self._parse_log_line(line))

                return {
                    "lines": parsed_lines,
                    "position": new_position,
                    "file": log_file,
                }
        except Exception as e:
            return {"error": str(e), "lines": [], "position": last_position}

    def _parse_log_line(self, line):
        result = {"time": "", "level": "INFO", "name": "", "message": line}
        parts = line.split(" ", 5)
        if len(parts) >= 5:
            if len(parts[0]) == 10 and "-" in parts[0]:
                result["time"] = f"{parts[0]} {parts[1]}"
                if parts[3] in ("INFO", "WARNING", "ERROR", "DEBUG", "CRITICAL"):
                    result["level"] = parts[3]
                    result["name"] = parts[4] if len(parts) > 4 else ""
                    result["message"] = parts[5] if len(parts) > 5 else ""
                    result["name"] = parts[4] if len(parts) > 4 else ""
                    result["message"] = parts[5] if len(parts) > 5 else ""
        return result

    @api.model
    def get_cache_info_rpc(self, model, record_id):
        """
        Wrapper to get cache info via ORM call (since RPC service might be unavailable in JS)
        """
        if not self.env.user.has_group("base.group_system"):
            raise Exception("Access Denied")
        return get_cache_info(self.env, model, record_id)

    @api.model
    def get_view_inheritance_rpc(self, view_id):
        """
        Returns the inheritance tree for a view.
        """
        if not self.env.user.has_group("base.group_system"):
            raise Exception("Access Denied")
        from .debug_tools import get_view_inheritance

        return get_view_inheritance(self.env, view_id)

    @api.model
    def search_views_rpc(self, query):
        """
        Searches for views by name, xml_id, or model.
        Returns top 20 results.
        """
        if not self.env.user.has_group("base.group_system"):
            raise Exception("Access Denied")

        domain = ["|", ("name", "ilike", query), ("model", "ilike", query)]
        # Try to search by ID if query is numeric
        if query.isdigit():
            domain = ["|"] + domain + [("id", "=", int(query))]

        views = self.env["ir.ui.view"].search_read(
            domain, ["id", "name", "model", "xml_id", "priority", "type"], limit=20
        )
        return views

    @api.model
    def get_view_diff_rpc(self, view_id):
        """
        Returns a unified diff between the view's resolved arch and its parent's resolved arch.
        """
        if not self.env.user.has_group("base.group_system"):
            raise Exception("Access Denied")

        view = self.env["ir.ui.view"].browse(int(view_id))
        if not view.exists():
            return ["View not found"]

        def get_arch_string(xml):
            if not isinstance(xml, str):
                xml = etree.tostring(xml, encoding="unicode", pretty_print=True)
            return xml

        # Get 'After' state: Standard resolved arch (includes this view and its parents)
        # Note: If there are OTHER children that inherit this view, they are also included!
        # Ideally we want: Parent + This View (only).
        # But for now, let's assume 'read_combined' gives the "Current System State" which is acceptable as "After".
        try:
            # Use _get_combined_arch to get the full resolved arch up to this point
            arch_after_xml = view._get_combined_arch()
            arch_after = get_arch_string(arch_after_xml)
        except Exception as e:
            return [f"Error resolving view: {e}"]

        # Get 'Before' state: The parent's resolved architecture WITHOUT this view.
        # If we just ask parent._get_combined_arch(), it MIGHT include this view if Odoo has already cached/applied it!
        # To be safe, we must manually apply inheritance up to the parent.

        if view.inherit_id:
            try:
                # 1. Get Base Arch (Root Parent)
                # We traverse up to find the root
                root = view.inherit_id
                while root.inherit_id:
                    root = root.inherit_id

                # 2. Collect all views in the inheritance chain of the PARENT
                # (excluding the current view 'view')
                # Odoo's _get_combined_arch internal logic is complex.
                # Let's try a simpler approach:
                # Parent's combined arch usually includes all children.
                # We need to SUBTRACT 'view' from 'parent'. Impossible.
                # We must REBUILD 'parent' without 'view'.

                # Retrieve all views that contribute to Parent, excluding 'view' and its children.
                # Actually, simpler:
                # arch_before = parent._get_combined_arch()
                # If this returns identical to arch_after, it means parent ALREADY merged 'view'.
                # In that case, we are Doomed unless we rebuild.

                # Rebuild Strategy:
                # Start with Root Arch.
                # Iterate all children of Root that are part of parent's hierarchy OR are siblings,
                # BUT SKIP 'view'.

                # This is too complex for this context.
                # Let's try relying on Odoo's `read_combined` behavior.
                # If they are identical, it means implicit merge.

                # HACK: If they are identical, assume 'Before' is simply 'After' minus the 'arch' of the current view applied?
                # No, xpath removal is hard.

                # Let's try to fetch parent arch ignoring the current view ID if possible? No API for that.

                # Manual Rebuild (simplified):
                # 1. Base Arch
                base_arch = etree.fromstring(root.arch)
                # 2. Get all inheriting views for Root
                # active_model check?
                all_inheriting = self.env["ir.ui.view"].search(
                    [
                        ("id", "!=", view.id),  # EXCLUDE SELF
                        ("mode", "=", "extension"),
                        ("inherit_id", "child_of", root.id),
                        ("model", "=", root.model),  # Ensure same model
                    ],
                    order="priority, id",
                )

                # Filter out 'view' and any of its descendents if necessary?
                # For now just exclude self.

                # Filter: We only want views that are "ancestors" of our conceptual "Before" state?
                # No, we want "System State if this view didn't exist".
                # So we apply ALL other views.

                combined_arch = base_arch
                for extension in all_inheriting:
                    # Skip if extension depends on 'view' (descendant)
                    # Checking if 'view' is an ancestor of 'extension'
                    # Traversing up extension.inherit_id...
                    is_descendant = False
                    curr = extension.inherit_id
                    while curr:
                        if curr.id == view.id:
                            is_descendant = True
                            break
                        curr = curr.inherit_id

                    if is_descendant:
                        continue

                    # Apply
                    try:
                        ext_arch = (
                            etree.fromstring(extension.arch_db)
                            if isinstance(extension.arch_db, str)
                            else extension.arch_db
                        )
                        combined_arch = self.env["ir.ui.view"].apply_inheritance_specs(
                            combined_arch, ext_arch, extension.id
                        )
                    except Exception:
                        pass  # Skip views that fail to apply

                arch_before = get_arch_string(combined_arch)
                from_name = f"{view.inherit_id.name or 'Parent'} (Reconstructed)"

            except Exception as e:
                arch_before = str(e)
                from_name = "Parent (Error)"
        else:
            arch_before = ""
            from_name = "Base View (New)"

        to_name = f"{view.name or 'View'} (Resolved)"

        # Generate Diff
        # splitlines(keepends=True) is important for unified_diff
        diff = list(
            difflib.unified_diff(
                arch_before.splitlines(keepends=True),
                arch_after.splitlines(keepends=True),
                fromfile=from_name,
                tofile=to_name,
            )
        )

        # If no diff (identical), return message
        if not diff:
            return [
                "Views are identical (No functional changes in this inheritance level)"
            ]

        return diff

    @api.model
    def get_model_relations_rpc(self, model_name):
        """
        Returns info about relational fields (M2o, O2m, M2m) for a given model.
        """
        if not self.env.user.has_group("base.group_system"):
            raise Exception("Access Denied")

        if model_name not in self.env:
            return {"error": f"Model '{model_name}' not found."}

        Model = self.env[model_name]
        fields_info = Model.fields_get(
            attributes=["type", "relation", "string", "help"]
        )

        relations = []
        for field_name, info in fields_info.items():
            if info["type"] in ("many2one", "one2many", "many2many"):
                relations.append(
                    {
                        "name": field_name,
                        "string": info["string"],
                        "type": info["type"],
                        "relation": info["relation"],
                        "help": info.get("help", ""),
                    }
                )

        return {
            "model": model_name,
            "description": Model._description,
            "relations": relations,
        }

    @api.model
    def profile_rpc(self, code):
        """
        Executes code and returns performance statistics (SQL count, time).
        """
        if not self.env.user.has_group("base.group_system"):
            raise Exception("Access Denied")

        # Prepare execution environment
        # We MUST use a new cursor because Profiler might close it or leave it in a bad state.
        # Also, we want to isolate the profiling from the current request transaction.
        stdout = io.StringIO()

        # Profile execution
        profiler = Profiler()
        start_time = time.time()

        error = None
        new_cr = self.pool.cursor()

        try:
            # Create a new environment with the new cursor
            new_env = api.Environment(new_cr, self.env.uid, self.env.context)

            # Construct execution context manualy since we don't have a helper method
            # We want to provide the standard shell environment
            safe_eval_context = {
                "env": new_env,
                "self": self,  # This is the web.shell.console model, which is fine
                "models": models,
                "fields": fields,
                "api": api,
                # We do NOT include SESSION_LOCALS here by default to keep profiling clean and isolated
                # If we wanted user vars, we'd need to fetch them from SESSION_LOCALS.
                # For now, let's keep it pure.
            }

            with contextlib.redirect_stdout(stdout):
                with profiler:
                    exec(code, safe_eval_context)

        except Exception:
            error = traceback.format_exc()
        finally:
            # ALWAYS ROLLBACK to ensure no side effects
            new_cr.rollback()
            new_cr.close()

        end_time = time.time()

        # Process profiler data
        total_queries = 0
        query_details = []

        # Odoo 17 Profiler stores SQL entries in profiler.entries
        # or we might need to check profiler.get_stats()
        entries = getattr(profiler, "entries", [])
        if not entries and hasattr(profiler, "content"):
            # Fallback for older/other Odoo versions if applicable
            entries = profiler.content.get("queries", [])

        for entry in entries:
            query = entry.get("query") or entry.get("sql")
            if query:
                total_queries += 1
                query_details.append(
                    {
                        "sql": query,
                        "time": entry.get("time", 0),
                    }
                )

        return {
            "total_time": (end_time - start_time) * 1000,  # ms
            "total_queries": total_queries,
            "queries": query_details,
            "error": error,
            "results": stdout.getvalue(),
        }
