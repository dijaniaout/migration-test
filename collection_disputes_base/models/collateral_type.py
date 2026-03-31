from odoo import models, fields

class CollateralType(models.Model):
    _name = 'collection_disputes_base.collateral_type'
    _description = 'Collateral Type'

    name = fields.Char('Nom', required=True)
    is_transferable = fields.Boolean('Transférable')
