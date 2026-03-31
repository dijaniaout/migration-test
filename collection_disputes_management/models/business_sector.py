from odoo import api, fields, models

class BusinessSector(models.Model):
    _name = "collection_disputes_management.business_sector"
    _description = "Secteur d'activité"
    name = fields.Char(string=u"Secteur d'activité", required=True)