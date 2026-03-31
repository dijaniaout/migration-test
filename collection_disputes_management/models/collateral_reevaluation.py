from odoo import models, fields,api

class CollateralReevaluation(models.Model):
    _name = 'collection_disputes_management.collateral_reevaluation'
    _description = 'Réévaluation de Garantie'

    collateral_id = fields.Many2one('collection_disputes_management.collateral', string='Garantie', required=True)
    reevaluation_date = fields.Date('Date de réévaluation', required=True)
    justification = fields.Text('Justificatif')
    new_value = fields.Float('Nouvelle valeur', required=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'collateral_reevaluation_ir_attachment_rel',
        'reevaluation_id', 'attachment_id',
        string='Documents justificatifs',
        domain="[('res_model', '=', 'collection_disputes_management.collateral_reevaluation')]"
    )
