# -*- coding: utf-8 -*-
{
    'name': 'TO MIGRATE: Gestion du découpage administratif du Sénégal',
    'version': '1.0',
    'summary': """Module pour la gestion du découpage administratif du Sénégal.""",
    'description': """
        Ce module permet la gestion du découpage administratif du Sénégal à savoir :
            - les régions
            - les départements
            - les communes
    """,
    'category': 'Productivity',
    'author': 'Baamtu',
    'maintainer': 'Baamtu',
    'website': 'http://www.baamtu.com',
    'license': 'LGPL-3',
    'depends': [ 'base'],
    'data': [
        'security/ir.model.access.csv',
        'data/region.xml',
        'data/department.xml',
        'data/municipality.xml',
        'views/menu.xml',
        'views/region.xml',
        'views/department.xml',
        'views/municipality.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
