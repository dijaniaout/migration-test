# -*- coding: utf-8 -*-
{
    "name" : "Ijayo docx report",
    "version" : "1.0",
    "author" : "Tugende",
    "description": """Create report from docx templates""",
    'website': 'https://gotugende.com/',
    "category": "Reporting",
    "development_status": "Production/Stable",
    "external_dependencies": {"python": ['docxtpl']},
    "depends": ["base", "web"],
    'data': [
        'data/convert_pdf_config.xml',
        'data/gotenberg_pdf_url.xml',
    ],
    "demo": [],
    "installable": True,
    "assets": {
        "web.assets_backend": [
            "report_docx/static/src/js/report/action_manager_report.esm.js",
        ],
    },
    'license': 'Other proprietary'
}