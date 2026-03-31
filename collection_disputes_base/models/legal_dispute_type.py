from odoo import models, fields

class LegalDisputeType(models.Model):
    _name = 'collection_disputes_base.legal_dispute_type'
    _description = 'Type de Litige'
    
    name = fields.Char(string='Nom', required=True)

   