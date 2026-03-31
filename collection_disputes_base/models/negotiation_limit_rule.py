from odoo import models, fields, api

class NegotiationLimitRule(models.Model):
    _name = 'collection_disputes_base.negotiation_limit_rule'
    _description = "Règle de limite de négociation"

    name = fields.Char(string="Nom de la règle", required=True)
    justification_required = fields.Boolean(
        string="Justificatif obligatoire si dépassé", default=True
    )
    line_ids = fields.One2many(
        'collection_disputes_base.negotiation_limit_rule_line',
        'rule_id',
        string="Lignes de règle"
    )

    @api.model_create_multi
    def create(self, vals_list):
        rules = super().create(vals_list)
        for rule in rules:
            rule._generate_default_lines()
        return rules

    def _generate_default_lines(self):
        condition_types = [
            'principal',
            'interest_due',
            'late_interest',
            'commitment_fees',
            'agf_fees',
            'interest_rate',
            'late_interest_rate',
            'loan_duration',
            'other_fees',
        ]
        lines = []
        for ctype in condition_types:
            lines.append((0, 0, {
                'condition_type': ctype,
                'max_percentage': 50 if ctype in ('commitment_fees', 'late_interest') else 00.0
            }))
        self.write({'line_ids': lines})

class NegotiationLimitRuleLine(models.Model):
    _name = 'collection_disputes_base.negotiation_limit_rule_line'
    _description = "Ligne de règle de négociation"

    rule_id = fields.Many2one(
        'collection_disputes_base.negotiation_limit_rule',
        string="Règle",
        required=True,
        ondelete='cascade'
    )
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
    ], string="Type de condition", required=True)
    max_percentage = fields.Float(string="Pourcentage limite de l'abattement (%)", required=True)

