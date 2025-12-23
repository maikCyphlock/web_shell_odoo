{
    'name': "Web Shell",
    'summary': "Frontend Python Shell & Log Viewer",
    'description': """
        Provides a terminal interface to execute Python code
        and view logs directly from the Odoo web client.
    """,
    'author': "MAIKOL AGUILAR",
    'website': "https://github.com/maikCyphlock",
    'category': 'Technical',
    'version': '1.0',
    'depends': ['base', 'web', 'bus'],
    'data': [
        'security/ir.model.access.csv',
        'views/console_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'https://cdn.jsdelivr.net/npm/ace-builds@1.32.2/src-min-noconflict/ace.js',
            'web_shell/static/src/components/console/*',
            'web_shell/static/src/components/log_viewer/*',
        ],
    },
    'license': 'OPL-1',
}
