# -*- coding: utf-8 -*-
{
    'name': 'Gestion des validations sur le processus de traitement de dossiers',
    'version': '19.0.1.0.0',
    'summary': """Module pour la gestion des validations sur le processus de traitement de dossiers""",
    'description': """
        Ce module permet la gestion des validation sur le processus de traitement de dossiers
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
        'views/step.xml',
        'views/work_document_to_validate.xml'
    ],
    'demo': [],
    'qweb': [],
    'images': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
