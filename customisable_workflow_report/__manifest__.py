# -*- coding: utf-8 -*-
{
    'name': 'Reporting sur la gestion du workflow',
    'version': '19.0.1.0.0',
    'summary': """Module de reporting sur le processus de traitement de dossiers""",
    'description': """
        Ce module permet de fare du reporting sur le processus de traitement de dossiers
    """,
    'category': 'Productivity',
    'author': 'Baamtu',
    'maintainer': 'Baamtu',
    'website': 'http://www.baamtu.com',
    'license': 'LGPL-3',
    'depends': [
        'base', 
        'customisable_workflow',
        'customisable_workflow_signature',
        'customisable_workflow_validation'
    ],
    'data': [
        'security/ir.model.access.csv'
    ],
    'assets': {
        'web.assets_backend': [
            'customisable_workflow_report/static/src/components/**/*'
        ]
    },
    'demo': [],
    'qweb': [],
    'images': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
