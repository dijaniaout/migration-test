# -*- coding:utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class Installment(models.Model):
    _name = 'collection_disputes_base.installment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = _("Échéances")
    _order = 'id desc'

    statement_id = fields.Many2one('loan.settlement.statement', string=_("Arrêté"), required=True, ondelete='cascade')

    statement_date = fields.Date( string=_("Date de l’échéance"), required=True)
    principal_due = fields.Float( string=_("Principal"), tracking=True)
    interest_due = fields.Float( string=_("Intérêts"), tracking=True)
    commitment_fees = fields.Float( string=_("Commissions d'engagement"), tracking=True)
    total = fields.Float( string=_("Total"), compute='_compute_total', store=True)
    number_of_days = fields.Integer( string=_("Jours"))
    late_interest = fields.Float( string=_("Intérêts de retard"), tracking=True)
    total_due = fields.Float( string=_("Montant Total"), compute='_compute_total_due', store=True)

    @api.depends('principal_due', 'interest_due', 'commitment_fees')
    def _compute_total(self):
        for rec in self:
            rec.total = (
                (rec.principal_due or 0.0)
                + (rec.interest_due or 0.0)
                + (rec.commitment_fees or 0.0)
            )

    @api.depends('total', 'late_interest')
    def _compute_total_due(self):
        for rec in self:
            rec.total_due = (rec.total or 0.0) + (rec.late_interest or 0.0)
