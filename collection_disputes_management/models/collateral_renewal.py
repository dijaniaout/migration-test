from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class CollateralRenewal(models.Model):
    _name = 'collection_disputes_management.collateral_renewal'
    _description = 'Renouvellement de Garantie'

    collateral_id = fields.Many2one(
        'collection_disputes_management.collateral', 
        string='Garantie', 
        required=True
    )
    renewal_date = fields.Date(
        string='Date de renouvellement',
        required=True,
        default=fields.Date.context_today
    )
    justification = fields.Text('Justificatif')

    # Nouvelle date d'expiration (calculée automatiquement)
    new_expiration_date = fields.Date(
        string="Nouvelle date d'expiration",
        compute="_compute_new_expiration_date",
        store=True
    )
    # Références d’inscription
    registration_reference = fields.Char("Références d'inscription ou d'opposabilité")
    # Rang
    rank = fields.Selection(
        selection=[(str(i), str(i)) for i in range(1, 11)],
        string="Rang de la garantie",
        help="Ordre de priorité de la garantie (1 = plus prioritaire, 10 = moins prioritaire)."
    )
    # Durée (en mois)
    duration_months = fields.Integer("Durée de la garantie (en mois)", required=True)
    # Obligé
    obligee_id = fields.Many2one(
        'res.partner', 
        string="Obligé", 
        help="L'entité obligée (ex: Banque teneuse de compte)"
    )
    # Montant inscrit/couvert ou garanti
    covered_amount = fields.Float("Montant inscrit/couvert ou garanti", required=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 
        'collateral_renewal_ir_attachment_rel',
        'renewal_id', 
        'attachment_id',
        string='Documents justificatifs',
        domain="[('res_model', '=', 'collection_disputes_management.collateral_renewal')]"
    )

    @api.depends('renewal_date', 'duration_months')
    def _compute_new_expiration_date(self):
        for rec in self:
            if rec.renewal_date and rec.duration_months:
                rec.new_expiration_date = rec.renewal_date + relativedelta(months=rec.duration_months)
            else:
                rec.new_expiration_date = False
