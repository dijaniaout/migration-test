#-*- coding:utf-8 -*-
from odoo import models, fields, api,  _
import logging
from datetime import timedelta
_logger = logging.getLogger(__name__)

class JusticeIntervention(models.Model):
    _name = 'collection_disputes_management.justice_intervention'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "date_start asc, date_end asc"
    _description = "Interventions de Justice"
    
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
        ('planned', 'Planifié'),
        ('in_progress', 'En cours'),
        ('blocked', 'Bloqué'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé')
    ], string="Statut", default='draft', tracking=True)    
    number_of_days = fields.Integer("Nombre de jours", compute='_compute_number_of_days', store=True)
    number_of_days_late = fields.Integer("Nombre de jours de retard", compute='_compute_number_of_days_late', store=True)
    dispute_case_id = fields.Many2one('collection.dispute.case', string='Dossier de recouvrement')
    legal_dispute_id = fields.Many2one('collection_disputes_management.legal_dispute', string='Dossier de litige')
    intervention_type_id = fields.Many2one('collection_disputes_management.intervention_type', string="Type d'intervention", required=True)
    note = fields.Html('Notes')
    supporting_document_ids = fields.Many2many(
        'ir.attachment',
        'justice_intervention_attachment_rel',
        string="Documents")
    line_type_id = fields.Many2one(
        related='intervention_type_id',
        store=True,
        string="Type d’intervention (affichage CV)"
        )
    date_end = fields.Date(string=u"Date de fin", compute="_compute_end_date", store=True)
    # Used to apply specific template on a line
    display_type = fields.Selection([('classic', 'Classic')], string="Display Type", compute='_compute_display_type')
    # Used to display the stakholder name in the widget
    description = fields.Char(string="Description", help="Description de l'intervention", related='stakeholder_id.name')
    assignment_letter_ref = fields.Char(u"Références de la lettre de mission de l’intervenant")

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
    

    @api.depends('state', "real_date_end", "expected_end_date" )
    def _compute_end_date(self):
        for record in self:
            if record.state == "draft":
                record.date_end = record.expected_end_date
            elif record.state == "done":
                record.date_end = record.real_date_end
    
    def _compute_display_type(self):
        for record in self:
            record.display_type = 'classic'

