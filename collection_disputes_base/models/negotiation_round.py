#-*- coding:utf-8 -*-
from odoo import models, fields, api,  _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class NegotiationRound(models.Model):
    _name = 'collection_disputes_base.negotiation_round'
    _description = "Round de négociation"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    agreement_id = fields.Many2one('collection_disputes_base.transaction_agreement', string="Accord transactionnel", required=True, ondelete='cascade')
    name = fields.Char(string="Nom", required=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('in_progress', 'En cours'),
        ('validated', 'Validé'),
        ('rejected', 'Non-accord'),
    ], string="Statut", default='draft', tracking=True)

    line_ids = fields.One2many(
        'collection_disputes_base.negotiation_round_line',
        'round_id',
        string="Conditions", compute='_generate_condition_lines', store=True
    )
    remboursement_freq = fields.Selection([
        ('mensuel', 'Mensuel'),
        ('trimestriel', 'Trimestriel'),
        ('semestriel', 'Semestriel')
    ], string="Fréquence de remboursement")
    duree = fields.Integer(string="Durée (mois)")
    negotiation_date = fields.Date("Date de la négociation", default=fields.Date.context_today)
    current_value_date = fields.Date("Date de la valeur actuelle")

    limit_rule_id = fields.Many2one('collection_disputes_base.negotiation_limit_rule',string="Règle de limite appliquée")
            
    @api.model_create_multi
    def create(self, vals_list):
        rounds = super().create(vals_list)
        return rounds

    @api.depends('agreement_id', 'limit_rule_id')
    def _generate_condition_lines(self):
        for record in self:
            if record.agreement_id and record.limit_rule_id:
                types = [
                    'principal', 'interest_due', 'late_interest', 'commitment_fees',
                    'agf_fees', 'interest_rate', 'late_interest_rate', 'loan_duration', 'other_fees',
                ]
                record.line_ids = [(5, 0, 0)] + [(0, 0, {'condition_type': t}) for t in types]

    @api.constrains('state')
    def _check_unique_validated_round(self):
        for rec in self:
            if rec.state == 'validated':
                rounds = self.search([
                    ('agreement_id', '=', rec.agreement_id.id),
                    ('state', '=', 'validated'),
                    ('id', '!=', rec.id)
                ])
                if rounds:
                    raise ValidationError("Il ne peut y avoir qu'un seul round validé pour un accord transactionnel.")

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            # If the state is changed to 'validated' -> update the agreement
            if vals.get('state') == 'validated':
                rec._update_agreement_from_lines()
        return res
    
    def _update_agreement_from_lines(self):
        mapping = {
            'principal': 'principal',
            'interest_due': 'interest',
            'late_interest': 'late_interest_agreement',
            'commitment_fees': 'commitment_fees_agreement',
            'agf_fees': 'agf_fees_agreement',
            'other_fees': 'other_fees_agreement',
            'interest_rate': 'interest_rate',
            'late_interest_rate': 'late_interest_rate',
            'loan_duration': 'duree',
        }

        for round in self:
            agreement = round.agreement_id
            if not agreement:
                continue

            signature_date = agreement.signature_date or fields.Date.context_today(self)

            updates = {
                'duree': round.duree,
                'remboursement_freq': round.remboursement_freq,
                'first_payment_date': (signature_date + relativedelta(months=1)).replace(day=1),
            }

            for line in round.line_ids:
                field_name = mapping.get(line.condition_type)
                if field_name:
                    updates[field_name] = line.agreement_amount

            if updates:
                agreement.write(updates)
    
class NegotiationRoundLine(models.Model):
    _name = 'collection_disputes_base.negotiation_round_line'
    _description = "Condition du round de négociation"

    round_id = fields.Many2one('collection_disputes_base.negotiation_round', string="Round", ondelete='cascade', required=True)
    condition_type = fields.Selection([
        ('principal', 'Principal'),
        ('interest_due', 'Intérêts'),
        ('late_interest', 'Intérêts de retard'),
        ('commitment_fees', 'Commissions d\'engagement'),
        ('agf_fees', 'Commissions AGF'),
        ('interest_rate', "Taux d'intérêt"),
        ('late_interest_rate', "Taux d'intérêt de retard"),
        ('loan_duration', 'Durée de la créance (mois)'),
        ('other_fees', 'Autres frais'),
    ], string="Type d'information")

    current_value = fields.Float(string="Valeur actuelle", compute='_compute_current_value', store=True, readonly=False)
    debtor_proposal = fields.Float(string="Proposition du débiteur")
    bank_proposal = fields.Float(string="Proposition de la banque")
    agreement_amount = fields.Float(string="Montant d’accord")
    limit = fields.Float(string="Limite", compute='_compute_limit', store=True)
    justificatif = fields.Binary(string="Justificatif", attachment=True)
    is_within_limit = fields.Boolean(string="Respect de la limite", compute="_compute_within_limit")
    abatement_percent = fields.Float(
        string="Abattement (%)",
        compute="_compute_abatement_percent",
        store=True,
        digits=(16, 2),
        help="((Valeur actuelle - Valeur accordée) / Valeur actuelle) * 100"
    )
    max_percentage = fields.Float(string="Pourcentage limite de l'abattement (%)", compute='_compute_max_percentage')

    @api.depends('current_value', 'agreement_amount')
    def _compute_abatement_percent(self):
        for rec in self:
            cv = rec.current_value or 0.0
            aa = rec.agreement_amount or 0.0
            if cv > 0:
                rec.abatement_percent = ((cv - aa) / cv) * 100.0
            else:
                rec.abatement_percent = 0.0

    @api.depends('agreement_amount', 'limit')
    def _compute_within_limit(self):
        for rec in self:
            rec.is_within_limit = rec.agreement_amount <= rec.limit if rec.limit else True

    @api.constrains('agreement_amount', 'limit', 'justificatif')
    def _check_justificatif_if_limit_exceeded(self):
        for rec in self:
            if rec.agreement_amount and rec.limit and rec.limit > rec.agreement_amount  and not rec.justificatif:
                raise ValidationError("Un justificatif est obligatoire si le montant de l'accord dépasse la limite. ")
    
    @api.depends('condition_type', 'round_id.agreement_id')
    def _compute_current_value(self):
        mapping = {
            'principal': 'principal_due',
            'interest_due': 'interest_due',
            'late_interest': 'late_interest',
            'commitment_fees': 'commitment_fees',
            'agf_fees': 'agf_fees',
            'other_fees': 'other_fees',
            'interest_rate': 'interest_rate',
            'late_interest_rate': 'late_interest_rate',
            'loan_duration': 'duree',
        }

        for rec in self:
            agreement = rec.round_id.agreement_id
            if not agreement:
                rec.current_value = 0.0
                continue

            field_name = mapping.get(rec.condition_type)
            rec.current_value = getattr(agreement, field_name, 0.0) or 0.0

    @api.depends('condition_type', 'round_id.limit_rule_id.line_ids', 'current_value')
    def _compute_limit(self):
        for rec in self:
            rec.limit = 0.0
            rule = rec.round_id.limit_rule_id
            if not rule or not rec.condition_type or not rec.current_value:
                continue
            rule_line = rule.line_ids.filtered(lambda l: l.condition_type == rec.condition_type)
            if rule_line:
                rec.limit = rec.current_value * (1 - (rule_line[0].max_percentage / 100))


    @api.depends('condition_type', 'round_id.limit_rule_id.line_ids', 'round_id.limit_rule_id.line_ids.max_percentage' )
    def _compute_max_percentage(self):
        for rec in self:
            rec.max_percentage = 0.0
            rule = rec.round_id.limit_rule_id
            if not rule or not rec.condition_type:
                continue
            rule_line = rule.line_ids.filtered(lambda l: l.condition_type == rec.condition_type)
            if rule_line:
                rec.max_percentage = rule_line.max_percentage

