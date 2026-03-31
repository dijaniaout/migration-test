from odoo import models, fields, api,  _
from dateutil.relativedelta import relativedelta
from math import ceil

FREQ_MAP = {
    'mensuel':  {'per_year': 12, 'months_per_period': 1},
    'trimestriel': {'per_year': 4,  'months_per_period': 3},
    'semestriel':  {'per_year': 2,  'months_per_period': 6},
}

class TransactionAgreement(models.Model):
    _name = 'collection_disputes_base.transaction_agreement'
    _description = "Accord transactionnel"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nom de l'accord", required=True, tracking=True)
    dispute_case_id = fields.Many2one('collection.dispute.case',string="Dossier de recouvrement",required=True,ondelete='cascade',tracking=True)

    # Arrêté sélectionné (lié)
    settlement_statement_id = fields.Many2one(
        'loan.settlement.statement',
        string="Dernier arrêté",
        domain="[('dispute_case_id', '=', dispute_case_id)]",
        tracking=True
    )
    currency_id = fields.Many2one('res.currency', string="Devise de l'arrêté", related='dispute_case_id.currency_id', store=True)

    # Champs liés à l’arrêté (affichés dans la vue)
    statement_date = fields.Date(related='settlement_statement_id.statement_date', string="Date de l'arrêté", readonly=True)
    statement_type = fields.Selection(related='settlement_statement_id.statement_type', string="Type d'arrêté", readonly=True)
    principal_due = fields.Monetary(related='settlement_statement_id.principal_due', string="Principal dû", readonly=True)
    other_fees = fields.Monetary(related='settlement_statement_id.other_fees', string="Autres frais", readonly=True)
    # Accord transactionnel
    duree = fields.Integer(string="Durée (mois)")
    remboursement_freq = fields.Selection([
        ('mensuel', 'Mensuel'),
        ('trimestriel', 'Trimestriel'),
        ('semestriel', 'Semestriel')
    ], string="Fréquence de remboursement")
    principal = fields.Monetary(string="Principal dû", tracking=True)
    other_fees_agreement = fields.Monetary(string="Autres frais")
    first_payment_date = fields.Date(string="Première échéance")
    amortization_type = fields.Selection([
        ('fixed_amount', 'Montant fixe par échéance'),
        ('fixed_principal', 'Amortissement fixe par échéance')
    ], string="Type d'amortissement", default='fixed_amount')

    # Statut de l’accord
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('in_progress', 'En cours'),
        ('validated_hd', 'Validé par la HD'),
        ('cancelled', 'Annulé')
    ], string="Statut", default='draft', tracking=True)
    document_ids = fields.Many2many('ir.attachment', 'document_attachment_rel', string="Documents")
    negotiation_round_ids = fields.One2many('collection_disputes_base.negotiation_round', 'agreement_id', string="Rounds de négociation")
    amortization_line_ids = fields.One2many('collection_disputes_base.amortization_line','agreement_id', string="Echéances / Paiements")
    agreement_type = fields.Selection([('with_partner', 'Avec Tiers'),('without_partner', 'Sans Tiers'),], string="Type d'accord", required=True)
    partner_ids = fields.Many2many('res.partner','transaction_agreement_partner_rel', string="Tiers concernés")

    settlement_total_due = fields.Monetary(string="Montant à recouvrer (dernier arrêté)", currency_field='currency_id', compute='_compute_followup_amounts', store=True, tracking=True,
        help="Montant à recouvrer (dernier arrêté)"
    )
 
    amount_to_recover_agreement = fields.Monetary(
        string="Montant à recouvrer (accord validé)",
        currency_field='currency_id',
        compute="_compute_followup_amounts",
        store=True,
        readonly=True,
    )

    amount_unrecoverable = fields.Monetary(
        string="Créance irrécouvrable",
        currency_field='currency_id',
        compute="_compute_followup_amounts",
        store=True,
        readonly=True,
        help="Différence entre le montant à recouvrer selon le dernier arrêté et celui selon l’accord validé."
    )
    
    # Montant à recouvrer (global) :
    # - avant accord validé  -> montant du dernier arrêté
    # - après accord validé  -> montant selon l’accord (échéances non payées)
    amount_to_recover = fields.Monetary(
        string="Montant à recouvrer",
        currency_field='currency_id',
        compute="_compute_amount_to_recover",
        store=True,
        readonly=True,
    )
    total_recovered = fields.Monetary(string="Montant total recouvré", compute='_compute_total_recovered', store=True, readonly=True)
    signature_date = fields.Date(
        string="Date de signature",
        tracking=True
    )
    
    # Montant forfaitaire avant échéances
    forfaitary_payment_amount = fields.Monetary(
        string="Montant forfaitaire initial",
        currency_field='currency_id',
        tracking=True,
        help="Montant à payer avant le début des échéances."
    )
    forfaitary_payment_due_date = fields.Date(
        string="Date du paiement forfaitaire",
        tracking=True,
        help="Date limite de paiement du montant forfaitaire initial."
    )
    
    @api.depends('amortization_line_ids.amount', 'amortization_line_ids.status')
    def _compute_total_recovered(self):
        for rec in self:
            total = sum(
                line.amount for line in rec.amortization_line_ids if line.status == 'paid'
            )
            rec.total_recovered = total
    
    @api.depends(
        'settlement_statement_id.total_due',
        'amortization_line_ids.amount',
        'amortization_line_ids.status',
        'state'
    )
    def _compute_followup_amounts(self):
        """Calcule les montants de suivi du prêt."""
        for rec in self:
            # 1 Montant du dernier arrêté
            amount_statement = rec.settlement_statement_id.total_due or 0.0

            # 2️ Montant selon accord validé (somme des échéances non payées)
            amount_agreement = 0.0
            if rec.state == 'validated_hd' and rec.amortization_line_ids:
                amount_agreement = sum(
                    l.amount or 0.0
                    for l in rec.amortization_line_ids
                    if l.status != 'paid'
                )

            # 3️ Créance irrécouvrable  
            unrecoverable = 0.0
            if amount_statement and amount_agreement:
                unrecoverable = amount_statement - amount_agreement

            rec.settlement_total_due = amount_statement
            rec.amount_to_recover_agreement = amount_agreement
            rec.amount_unrecoverable = unrecoverable
                
    @api.depends('state', 'settlement_statement_id.total_due', 'amortization_line_ids.amount', 'amortization_line_ids.status')
    def _compute_amount_to_recover(self):
        for rec in self:
            # 1) Montant selon dernier arrêté
            amount_statement = rec.settlement_statement_id.total_due or 0.0

            # 2) Montant selon accord validé = somme des échéances non payées
            amount_agreement = 0.0
            if rec.state == 'validated_hd' and rec.amortization_line_ids:
                amount_agreement = sum(
                    (l.amount or 0.0)
                    for l in rec.amortization_line_ids
                    if l.status != 'paid'
                )

            # 3) Choix du montant à recouvrer
            if rec.state == 'validated_hd':
                # s’il n’y a pas encore de lignes, on retombe sur l’arrêté
                rec.amount_to_recover = amount_agreement or amount_statement
            else:
                rec.settlement_total_due = rec.settlement_statement_id.total_due or 0.0
                
                
    def _get_period_params(self):
        freq = self.remboursement_freq or 'mensuel'
        cfg = FREQ_MAP.get(freq, FREQ_MAP['mensuel'])
        return cfg['per_year'], cfg['months_per_period']

    def _get_new_principal(self):
        """Calcule le nouveau principal P (somme des composantes dues)."""
        self.ensure_one()
        P = 0.0
        P += (self.principal or 0.0)
        return P
    
    def _compute_annuity(self, P, number_of_installments, amortization_type='fixed_amount'):
        """Renvoie la mensualité/échéance M selon la formule d’annuité."""
        if P <= 0 or number_of_installments <= 0:
            return 0.0
       
        return P / number_of_installments

    def _first_due_date(self):
        self.ensure_one()
        return self.first_payment_date or fields.Date.context_today(self)

    def action_generate_amortization(self):
        """Génère le tableau d’amortissement tenant compte du paiement forfaitaire."""
        for rec in self:
            rec.amortization_line_ids.unlink()

            per_year, months_per_period = rec._get_period_params()
            n = int(ceil((rec.duree or 0) / float(months_per_period))) if rec.duree else 0
            P = rec._get_new_principal()

            if P <= 0 or n <= 0:
                continue

            currency = rec.currency_id or rec.env.company.currency_id
            round_amt = currency.round

            # Montant forfaitaire (s’il existe)
            forfaitary = rec.forfaitary_payment_amount or 0.0
            effective_principal = P - forfaitary if forfaitary > 0 else P

            # Ligne spéciale : paiement forfaitaire
            lines_vals = []
            if forfaitary > 0:
                lines_vals.append({
                    'agreement_id': rec.id,
                    'date': rec.forfaitary_payment_due_date or fields.Date.context_today(rec),
                    'amount': round_amt(forfaitary),
                    'principal': round_amt(forfaitary),
                    'remaining_principal': round_amt(effective_principal),
                    'status': 'unpaid',
                })

            # Calcul de l’échéance (avec capital réduit)
            M = rec._compute_annuity(effective_principal, n)
            crd = effective_principal
            due_date = rec._first_due_date()
            for period in range(1, n + 1):
                if rec.amortization_type == 'fixed_principal':
                    principal_part = round_amt(effective_principal / n)
                    crd -= principal_part
                    interest = crd 
                    effective_amount = principal_part + interest
                else:
                    interest = crd 
                    principal_part = M - interest
                    if period == n:
                        principal_part = crd
                        effective_amount = principal_part + interest
                    else:
                        effective_amount = M

                    interest = round_amt(interest)
                    principal_part = round_amt(principal_part)
                    effective_amount = round_amt(effective_amount)
                    crd = round_amt(crd - principal_part)

                lines_vals.append({
                    'agreement_id': rec.id,
                    'date': due_date,
                    'amount': effective_amount,
                    'principal': principal_part,
                    'remaining_principal': crd if crd >= 0 else 0.0,
                    'status': 'unpaid',
                })
                due_date = due_date + relativedelta(months=+months_per_period)

            rec.env['collection_disputes_base.amortization_line'].create(lines_vals)