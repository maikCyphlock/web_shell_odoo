{
    "name": "Odoo DevTools",
    "summary": "Frontend Python Shell & Log Viewer (Development Tool)",
    "description": """
! ADVERTENCIA DE SEGURIDAD !
Este módulo permite ejecución de código Python arbitrario.
SOLO usar en entornos de desarrollo. NUNCA instalar en producción.

Características de seguridad:
- Audit logging de todos los comandos ejecutados
- Timeout configurable via ir.config_parameter 'web_shell.timeout' (default: 30s)
- Patrones bloqueados configurables via 'web_shell.blocked_patterns'
  (default: os.system, os.popen, subprocess, shutil.rmtree, __import__)

Solo usuarios con grupo 'Administration / Settings' pueden usar el shell.
    """,
    "author": "MAIKOL AGUILAR",
    "website": "https://github.com/maikCyphlock",
    "category": "Technical",
    "version": "1.1",
    "depends": ["base", "web", "bus"],
    "data": [
        "security/ir.model.access.csv",
        "views/console_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "https://cdn.jsdelivr.net/npm/ace-builds@1.32.2/src-min-noconflict/ace.js",
            "web_shell/static/src/components/console/*",
            "web_shell/static/src/components/log_viewer/*",
            "web_shell/static/src/components/debug_tools/*",
        ],
    },
    "license": "LGPL-3",
}
