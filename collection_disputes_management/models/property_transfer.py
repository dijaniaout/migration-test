#-*- coding:utf-8 -*-
from odoo import models, fields, api,  _
from datetime import timedelta


class PropertyTansfer(models.Model):
    _name = 'collection_disputes_management.property_transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "date_start asc, real_date_end asc"
    _description = " Transfert de propriété"
    
    name = fields.Char(string=u"Libellé", required=True)
    stakeholder_id = fields.Many2one(
        'res.partner',
        string="Intervenant",
        tracking=True
    )
    creation_date = fields.Date(string=u"Date de création", default=fields.Date.context_today)
    date_start = fields.Date(string=u"Date de début", required=True)
    expected_end_date = fields.Date(string=u"Date de fin prévisionnelle", required=True)
    real_date_end = fields.Date(string=u"Date de fin réelle")
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('in_progress', 'En cours'),
        ('acquired_property', 'Propriété Acquise'),
        ('transfer_heritage', 'Transfert au patrimoine'),
        ('registered_heritage', ' Inscrit au patrimoine'),
        ('cancelled', 'Annulé')
    ], string="Statut", default='draft', tracking=True)    
    number_of_days = fields.Integer("Nombre de jours", compute='_compute_number_of_days', store=True)
    number_of_days_late = fields.Integer("Nombre de jours de retard", compute='_compute_number_of_days_late', store=True)
    dispute_case_id = fields.Many2one('collection.dispute.case', string='Dossier de recouvrement')
    legal_dispute_id = fields.Many2one('collection_disputes_management.legal_dispute', string='Dossier de litige')
    note = fields.Html('Notes')
    supporting_document_ids = fields.Many2many(
        'ir.attachment',
        'property_transfer_attachment_rel',
        string="Documents")
    collateral_id = fields.Many2one('collection_disputes_management.collateral', string='Garantie')
    
    @api.depends("real_date_end", "date_start")
    def _compute_number_of_days(self):
        for record in self:
            if record.real_date_end and record.date_start:
                delta = record.real_date_end - record.date_start
                record.number_of_days = delta.days
            else:
                record.number_of_days = 0

    @api.depends("real_date_end", "expected_end_date")
    def _compute_number_of_days_late(self):
        for record in self:
            if record.real_date_end and record.expected_end_date:
                delay = (record.real_date_end - record.expected_end_date).days
                record.number_of_days_late = delay if delay > 0 else 0
            else:
                record.number_of_days_late = 0
    


