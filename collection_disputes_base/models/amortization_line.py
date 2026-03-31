from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class InstallmentLine(models.Model):
    _name = 'collection_disputes_base.amortization_line'
    _description = "Ligne d'amortissement"

    agreement_id = fields.Many2one(
        'collection_disputes_base.transaction_agreement',
        string="Accord", ondelete='cascade', required=False
    )
    case_id = fields.Many2one(
        'collection.dispute.case',
        string="Dossier", related="agreement_id.dispute_case_id", store=True, readonly=True
    )
    date = fields.Date(string="Date d'échéance", required=True)
    amount = fields.Monetary(string="Montant à rembourser", required=True)
    principal = fields.Monetary(string="Amortissement")
    interest = fields.Monetary(string="Intérêt")
    currency_id = fields.Many2one(
        'res.currency', string="Devise", related="agreement_id.currency_id", store=True, readonly=True
    )
    paid_amount = fields.Monetary( string="Montant payé", currency_field='currency_id', tracking=True, help="Montant payé partiellement ou totalement sur cette échéance.")
    payment_ref = fields.Char( string="Référence paiement", tracking=True, help="Numéro ou référence du paiement dans le système (virement, reçu, etc.)")
    payment_date = fields.Date(string="Date du paiement", tracking=True, help="Date à laquelle le paiement a été effectué.")
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'amortization_line_attachment_rel',
        'line_id', 'attachment_id',
        string="Documents de paiement"
    )
    status = fields.Selection([
        ('unpaid', 'Non payé'),
        ('partial', 'Partiellement payé'),
        ('paid', 'Payé'),
    ], string="Statut", compute="_compute_status", store=True, tracking=True)
    remaining_principal = fields.Monetary(string="Capital restant dû", currency_field='currency_id', readonly=True)

    @api.constrains('paid_amount', 'amount')
    def _check_paid_amount_not_exceed(self):
        for rec in self:
            if rec.paid_amount and rec.amount and rec.paid_amount > rec.amount:
                raise ValidationError(_(
                    "Le montant payé (%.2f) dépasse le montant de l’échéance (%.2f).\n"
                    "Veuillez reporter le surplus sur l’échéance suivante."
                ) % (rec.paid_amount, rec.amount))

    # --- LOGIQUE DE STATUT AUTOMATIQUE ---
    @api.depends('paid_amount', 'amount')
    def _compute_status(self):
        """Détermine automatiquement le statut selon le montant payé."""
        for rec in self:
            if not rec.paid_amount or rec.paid_amount == 0:
                rec.status = 'unpaid'
            elif rec.paid_amount < rec.amount:
                rec.status = 'partial'
            else:
                rec._check_paid_amount_not_exceed()
                rec.status = 'paid'

    @api.constrains('paid_amount')
    def _check_paid_amount(self):
        for rec in self:
            if rec.paid_amount and rec.paid_amount < 0:
                raise ValidationError(_("Le montant payé ne peut pas être négatif."))

