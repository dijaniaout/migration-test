# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "TO MIGRATE: Base report xlsx",
    "summary": "Base module to create xlsx report",
    "author": "ACSONE SA/NV," "Creu Blanca," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "category": "Reporting",
    "version": "17.0",
    "development_status": "Mature",
    "license": "AGPL-3",
    "external_dependencies": {"python": ["openpyxl","xlsxwriter", "xlrd"]},
    "depends": ["base", "web"],
    "demo": ["demo/report.xml"],
    "installable": True,
    "assets": {
        "web.assets_backend": [
            "report_xlsx/static/src/js/report/action_manager_report.esm.js",
        ],
    },
}
