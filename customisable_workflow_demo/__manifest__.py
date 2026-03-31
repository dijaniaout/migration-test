# -*- coding: utf-8 -*-
{
    'name': 'Module de démo de la gestion des processus',
    'version': '19.0.1.0.0',
    'summary': """Module de démo de la gestion des processus""",
    'description': """
        Module de démo de la gestion des processus
    """,
    'category': 'Productivity',
    'author': 'Baamtu',
    'maintainer': 'Baamtu',
    'website': 'http://www.baamtu.com',
    'license': 'LGPL-3',
    'depends': [ 'base',
                'customisable_workflow',
                'customisable_workflow_report',
                'customisable_workflow_validation',
                'customisable_workflow_signature',
                'workflow_checklist'
                ],
    'data': [
        'security/ir.model.access.csv',
        'data/step_decision_cron.xml',
        'views/work_demo.xml'
    ],
    'demo': [
        'demo/customisable_workflow_demo.xml'
    ],
    'qweb': [],
    'images': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
