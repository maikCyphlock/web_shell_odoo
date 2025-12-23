# -*- coding: utf-8 -*-
# Part of Web Shell. See LICENSE file for full copyright and licensing details.
# Created by MAIKOL AGUILAR (https://github.com/maikol-aguilar)

import os
import json
from odoo import http
from odoo.http import request

class LogViewerController(http.Controller):
    
    LOG_FILE_PATHS = [
        '/var/log/odoo/odoo-server.log',
        '/var/log/odoo/odoo.log',
        '/proc/1/fd/1',  # Docker stdout
        
    ]
    
    def _find_log_file(self):
        """Find an available log file"""
        for path in self.LOG_FILE_PATHS:
            if os.path.exists(path) and os.access(path, os.R_OK):
                return path
        return None

    @http.route('/web_shell/logs', type='json', auth='user')
    def get_logs(self, last_position=0, max_lines=100):
        """
        Fetch new log lines from the Odoo log file.
        Returns lines after the given position.
        """
        if not request.env.user.has_group('base.group_system'):
            return {'error': 'Access Denied', 'lines': [], 'position': 0}
        
        log_file = self._find_log_file()
        
        if not log_file:
            return {'error': 'Log file not found', 'lines': [], 'position': 0}
        
        try:
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                # Get file size
                f.seek(0, 2)  # Go to end
                file_size = f.tell()
                
                if last_position == 0:
                    # First request: get last N lines
                    # Read from end backwards
                    read_size = min(50000, file_size)  # Read up to 50KB from end
                    f.seek(max(0, file_size - read_size))
                    content = f.read()
                    lines = content.strip().split('\n')[-max_lines:]
                    new_position = file_size
                elif last_position < file_size:
                    # Read new content since last position
                    f.seek(last_position)
                    content = f.read()
                    lines = content.strip().split('\n') if content.strip() else []
                    # Limit lines
                    lines = lines[-max_lines:] if len(lines) > max_lines else lines
                    new_position = file_size
                else:
                    # No new content (or file was rotated)
                    lines = []
                    new_position = file_size
                
                # Parse log lines into structured format
                parsed_lines = []
                for line in lines:
                    if line.strip():
                        parsed = self._parse_log_line(line)
                        parsed_lines.append(parsed)
                
                return {
                    'lines': parsed_lines,
                    'position': new_position,
                    'file': log_file
                }
                
        except Exception as e:
            return {'error': str(e), 'lines': [], 'position': 0}
    
    def _parse_log_line(self, line):
        """
        Parse a log line into structured format.
        Odoo logs typically look like:
        2025-12-21 02:51:41,106 1 INFO mecatec odoo.addons.base.models.ir_http: ...
        """
        result = {
            'time': '',
            'level': 'INFO',
            'name': '',
            'message': line
        }
        
        # Try to parse standard Odoo log format
        parts = line.split(' ', 5)
        if len(parts) >= 5:
            # Check if first part looks like a date
            if len(parts[0]) == 10 and '-' in parts[0]:
                result['time'] = f"{parts[0]} {parts[1]}"
                # parts[2] is PID, parts[3] is level
                if parts[3] in ('INFO', 'WARNING', 'ERROR', 'DEBUG', 'CRITICAL'):
                    result['level'] = parts[3]
                    result['name'] = parts[4] if len(parts) > 4 else ''
                    result['message'] = parts[5] if len(parts) > 5 else ''
        
        return result
