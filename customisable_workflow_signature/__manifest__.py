# -*- coding: utf-8 -*-
{
    'name': 'Gestion des signatures sur le processus de traitement de dossiers',
    'version': '19.0.1.0.0',
    'summary': """Module pour la gestion des signatures sur le processus de traitement de dossiers""",
    'description': """
        Ce module permet la gestion des signatures sur le processus de traitement de dossiers
    """,
    'category': 'Productivity',
    'author': 'Baamtu',
    'maintainer': 'Baamtu',
    'website': 'http://www.baamtu.com',
    'license': 'LGPL-3',
    'depends': [ 'base','customisable_workflow',
                #  'base_fontawesome'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_users.xml',
        'views/step.xml',
        'wizard/upload_signed_doc_wizard.xml',
        'views/work_signed_document.xml',
        'views/workflow.xml'
    ],
    'demo': [],
    'qweb': [],
    'images': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
