from odoo import api, fields, models

class LegalStatus(models.Model):
    _name = "collection_disputes_base.legal_status"
    _description = "Forme juridique"
    name = fields.Char(string=u"Forme juridique", required=True)