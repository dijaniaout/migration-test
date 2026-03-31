#-*- coding:utf-8 -*-
from odoo import models, fields, api,  _
import logging
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)

class LoanSettlementStatement(models.Model):
    _name = 'loan.settlement.statement'
    _description = "Loan Settlement Statement"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'statement_date desc'
    
    dispute_case_id = fields.Many2one('collection.dispute.case', string="Créance concerné", required=True, ondelete='cascade')
    disbursed_amount = fields.Monetary(string="Montant décaissé")
    statement_date = fields.Date(string="Date de l'arrêté", required=True)

    principal_due = fields.Monetary(string="Principal (part échue)", tracking=True)

    total_due = fields.Monetary(string="Montant créance à recouvrer", compute='_compute_total_due', store=True)
    other_fees = fields.Monetary(string="Autres frais dus", tracking=True)

    statement_type = fields.Selection(
        selection=[
            ('provisional', "Provisoire"),
            ('final', "Définitif")
        ],
        string="Type d'arrêté",
        default='provisional')

    
    name = fields.Char(string="Référence", compute="_compute_name", store=True)
    installment_ids = fields.One2many('collection_disputes_base.installment', 'statement_id', string='Échéances')
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'loan_settlement_statement_ir_attachment_rel',
        'statement_id',
        'attachment_id',
        string="Pièces jointes"
    )

    currency_id = fields.Many2one('res.currency', string="Devise de l'arrêté", default=lambda self: self.env.company.currency_id)


    @api.depends('statement_date', 'dispute_case_id', 'statement_type')
    def _compute_name(self):
        for record in self:
            date_str = record.statement_date.strftime('%d/%m/%Y') if record.statement_date else '??'
            type_label = dict(self._fields['statement_type'].selection).get(record.statement_type, '???')
            loan_ref = record.dispute_case_id.name or 'Prêt'
            record.name = f"{loan_ref} - {type_label} - {date_str}"
            
    @api.depends('principal_due')
    def _compute_total_due(self):
        for rec in self:
            rec.total_due = sum([rec.principal_due ])
                