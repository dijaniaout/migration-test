from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class JudicialDecision(models.Model):
    _name = 'collection_disputes_management.judicial_decision'
    _description = "Décision de justice"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'decision_date desc, id desc'

    name = fields.Char(
        string="Référence / Intitulé",
        help="Référence interne ou intitulé court de la décision.",
        tracking=True,
    )
    dispute_case_id = fields.Many2one('collection.dispute.case', string="Prêt concerné", ondelete='cascade')
    legal_dispute_id = fields.Many2one('collection_disputes_management.legal_dispute', string="Dossier de litige", ondelete='cascade')

    instance_level = fields.Selection(
        [
            ('first', "Première instance"),
            ('appeal', "Deuxième instance / Appel"),
            ('cassation', "Cassation / Suprême"),
            ('other', "Autre"),
        ],
        string="Instance",
        required=True,
        tracking=True,
        index=True,
    )
    decision_status = fields.Selection(selection=[
        ('pending', 'En attente'),
        ('won', 'Gagné'),
        ('lost', 'Perdu'), ('mixed', 'Partiellement favorable')], string='Statut de la décision', tracking=True, default='pending')
    decision_date = fields.Date(
        string="Date de la décision",
        tracking=True,
        default=fields.Date.context_today,
    )

    condemnation_ids = fields.One2many(
        'collection_disputes_management.judicial_decision_condemnation',
        'decision_id',
        string="Condamnations associées"
    )

    currency_id = fields.Many2one(
        'res.currency',
        string="Devise",
        related='dispute_case_id.currency_id',
        readonly=True,
        store=True,
    )

    comment = fields.Text(string="Commentaire général", help="Commentaire global sur la décision.")