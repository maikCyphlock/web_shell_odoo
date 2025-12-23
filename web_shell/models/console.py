# -*- coding: utf-8 -*-
# Part of Web Shell. See LICENSE file for full copyright and licensing details.
# Created by MAIKOL AGUILAR (https://github.com/maikol-aguilar)

import sys
import io
import traceback
import logging
from odoo import models, api, fields

_logger = logging.getLogger(__name__)

# Global session storage: {user_id: user_variables_dict}
# Warning: This is memory-only and per-worker. Multi-worker setups will have inconsistent state.
# We ONLY store user-defined variables here, NOT env or self (which are request-specific)
SESSION_LOCALS = {}

class WebShellConsole(models.Model):
    _name = 'web.shell.console'
    _description = 'Web Shell Console'

    @api.model
    def execute_command(self, code):
        """
        Executes python code and returns the output.
        """
        if not self.env.user.has_group('base.group_system'):
            raise Exception("Access Denied: You must be a system administrator to use the shell.")

        user_id = self.env.user.id
        
        # Initialize user session if needed (only user variables, no env/self!)
        if user_id not in SESSION_LOCALS:
            SESSION_LOCALS[user_id] = {}
        
        # Create execution context with FRESH env and self for THIS request
        # Merge with user's persistent variables
        execution_context = {
            'env': self.env,
            'self': self,
            'models': models,
            'fields': fields,
            'api': api,
            **SESSION_LOCALS[user_id]  # User variables overlay
        }

        # Capture stdout/stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture

        result = None
        try:
            # Try to eval first (for expressions), then exec (for statements)
            try:
                # Compile as 'eval' to see if it's an expression
                # This allows typing "1+1" and getting "2" without "print"
                compiled = compile(code, '<string>', 'eval')
                result_obj = eval(compiled, execution_context)
                if result_obj is not None:
                    print(repr(result_obj))
            except SyntaxError:
                # If it's not an expression, exec it
                exec(code, execution_context)
        except Exception:
            traceback.print_exc()
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        
        # Save back user-defined variables (exclude env, self, builtins, modules)
        # This preserves user variables across commands
        for key, value in execution_context.items():
            if key not in ('env', 'self', 'models', 'fields', 'api', '__builtins__'):
                SESSION_LOCALS[user_id][key] = value

        output = stdout_capture.getvalue() + stderr_capture.getvalue()
        return output

    @api.model
    def test_log(self):
        """Generates test logs at different levels"""
        logger = logging.getLogger('odoo.addons.web_shell')
        logger.info("Test INFO log from Web Shell")
        logger.warning("Test WARNING log from Web Shell")
        return True

    @api.model
    def read_logs(self, last_position=0, max_lines=100):
        """
        Reads logs directly from the Odoo log file.
        Returns: { 'lines': [...], 'position': new_pos, 'error': ... }
        """
        if not self.env.user.has_group('base.group_system'):
            raise Exception("Access Denied")

        import os
        
        LOG_FILE_PATHS = [
            '/var/log/odoo/odoo-server.log',
            '/var/log/odoo/odoo.log',
            '/proc/1/fd/1',
        ]
        
        log_file = None
        for path in LOG_FILE_PATHS:
            if os.path.exists(path) and os.access(path, os.R_OK):
                log_file = path
                break
        
        if not log_file:
            # Fallback if no log file found (dev environment)
            return {'lines': [], 'position': 0, 'error': "Log file not found"}

        try:
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                f.seek(0, 2)
                file_size = f.tell()
                
                if last_position == 0:
                    read_size = min(50000, file_size)
                    f.seek(max(0, file_size - read_size))
                    content = f.read()
                    lines = content.strip().split('\n')[-max_lines:]
                    new_position = file_size
                elif last_position < file_size:
                    f.seek(last_position)
                    content = f.read()
                    lines = content.strip().split('\n') if content.strip() else []
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
                    'lines': parsed_lines,
                    'position': new_position,
                    'file': log_file
                }
        except Exception as e:
            return {'error': str(e), 'lines': [], 'position': last_position}

    def _parse_log_line(self, line):
        result = {'time': '', 'level': 'INFO', 'name': '', 'message': line}
        parts = line.split(' ', 5)
        if len(parts) >= 5:
            if len(parts[0]) == 10 and '-' in parts[0]:
                result['time'] = f"{parts[0]} {parts[1]}"
                if parts[3] in ('INFO', 'WARNING', 'ERROR', 'DEBUG', 'CRITICAL'):
                    result['level'] = parts[3]
                    result['name'] = parts[4] if len(parts) > 4 else ''
                    result['message'] = parts[5] if len(parts) > 5 else ''
        return result
