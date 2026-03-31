#-*- coding:utf-8 -*-
from odoo import models, fields, api,  _
class PaymentIncident(models.Model):
    _name = 'payment.incident'
    _description = "Incident de Paiement"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'reception_date desc'

    name = fields.Char(string="Numéro de l'incident", required=True, copy=False, readonly=True, default=lambda self: _('New'))
    dispute_case_id = fields.Many2one('collection.dispute.case', string="Prêt concerné", ondelete='cascade')   
    project_code = fields.Char(string="Code du projet", required=True)
    payment_nature_id = fields.Many2one('payment.nature', string="Nature du paiement", required=True)
    reception_date = fields.Date(string="Date de réception", required=True, default=fields.Date.context_today)
    amount = fields.Float(string="Montant", required=True)
    issuing_bank = fields.Char(string="Banque émettrice")
    description = fields.Html(string="Description")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('payment.incident') or _('New')
        return super(PaymentIncident, self).create(vals)
