#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
class Commission(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'collection_disputes_management.other_commission'
    _description = "Commissions et autres frais dus"
    _order = 'id desc'
    
    name = fields.Char(u"Libellé")
    date = fields.Date(string="Date", required=True)
    amount = fields.Float(string="Commissions et autres frais dus", tracking=True)
    statement_id = fields.Many2one('loan.settlement.statement', string=u"Arrêté", required=True, ondelete='cascade')