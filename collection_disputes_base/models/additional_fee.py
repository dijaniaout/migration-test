from odoo import models, fields, api,  _

class AdditionalFee(models.Model):
    _name = 'collection_disputes_base.additional_fee'
    _description = "Frais annexes"

    dispute_case_id = fields.Many2one('collection.dispute.case', string="Dossier de recouvrement", ondelete='cascade')
    date = fields.Date(string="Date", default=fields.Date.context_today, required=True)
    amount = fields.Monetary(string="Montant", required=True)
    fee_type = fields.Selection([
        ('procedure', 'Frais de procédure'),
        ('honorary', 'Honoraires')
    ], string="Type", required=True, default='procedure')
    auxiliary_id = fields.Many2one('collection_disputes_base.justice_auxiliary', string="Auxiliaire de justice")
    attachment_ids = fields.Many2many('ir.attachment', string="Justificatifs")
    currency_id = fields.Many2one('res.currency', string="Devise", default=lambda self: self.env.company.currency_id)
    legal_dispute_id = fields.Many2one('collection_disputes_base.legal_dispute', string="Dossier de litige", ondelete='cascade')

