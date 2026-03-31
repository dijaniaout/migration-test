# -*- coding: utf-8 -*-
{
    'name': 'Checklist workfow',
    'version': '19.0.1.0.0',
    'summary': """Module checklist workfow """,
    'description': """
        Ce module permet de noter les questions sur l'ensemble des documents
    """,
    'category': 'Productivity',
    'author': 'Baamtu',
    'maintainer': 'Baamtu',
    'website': 'http://www.baamtu.com',
    'license': 'LGPL-3',
    'depends': [
        'customisable_workflow'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/check.xml',
        'views/section.xml',
        'views/checklist.xml',
        'views/step.xml',
        'views/checklist_response.xml',
    ],
    'demo': [],
    'qweb': [],
    'images': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
