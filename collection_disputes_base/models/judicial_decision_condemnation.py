from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class JudicialDecisionCondemnation(models.Model):
    _name = 'collection_disputes_base.judicial_decision_condemnation'
    _description = "Condamnation liée à une décision de justice"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    decision_id = fields.Many2one(
        'collection_disputes_base.judicial_decision',
        string="Décision de justice",
        required=True,
        ondelete='cascade',
        index=True,
    )

    name = fields.Char(
        string="Libellé",
        required=True,
        help="Libellé ou objet de la condamnation (ex: Dommages et intérêts, frais de justice, etc.)"
    )

    bank_claim_amount = fields.Monetary(
        string="Montant demandé par la banque",
        currency_field='currency_id',
        tracking=True,
        help="Montant réclamé initialement par la banque pour cette condamnation."
    )

    counterparty_claim_amount = fields.Monetary(
        string="Montant demandé par l'autre partie",
        currency_field='currency_id',
        tracking=True,
        help="Montant réclamé par la contrepartie pour cette condamnation."
    )

    amount_condemnation = fields.Monetary(
        string="Montant de la condamnation",
        currency_field='currency_id',
        tracking=True,
        help="Montant final condamné par la juridiction."
    )

    outcome = fields.Selection(
        [
            ('favorable', "Favorable"),
            ('unfavorable', "Défavorable"),
            ('mixed', "Partiellement favorable / mixte"),
        ],
        string="Issue",
        tracking=True,
        required=True,
        help="Issue de cette condamnation spécifique du point de vue."
    )

    currency_id = fields.Many2one(
        'res.currency',
        string="Devise",
        related='decision_id.currency_id',
        store=True,
        readonly=True,
    )

    comment = fields.Text(
        string="Commentaire",
        help="Observations ou précisions sur cette condamnation."
    )

    @api.constrains('amount_condemnation')
    def _check_amount_non_negative(self):
        for rec in self:
            if rec.amount_condemnation and rec.amount_condemnation < 0:
                raise ValidationError(_("Le montant de la condamnation ne peut pas être négatif."))
