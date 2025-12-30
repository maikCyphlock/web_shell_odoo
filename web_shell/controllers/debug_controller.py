# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from ..models.debug_tools import get_cache_info

class DebugController(http.Controller):

    @http.route('/web_shell/debug/cache_info', type='json', auth='user')
    def get_cache_info(self, model, record_id):
        if not request.env.user.has_group('base.group_system'):
            return {'error': 'Access Denied'}
        
        try:
            return get_cache_info(request.env, model, record_id)
        except Exception as e:
            return {'error': str(e)}
