#-*- coding:utf-8 -*-
from odoo import models, fields,api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta



class Collateral(models.Model):
    _name = 'collection_disputes_management.collateral'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Garantie'

    name = fields.Char('Numéro', required=True, copy=False, readonly=True, default='New')
    label = fields.Char('Libellé', required=True)
    type_id = fields.Many2one('collection_disputes_management.collateral_type', string='Type', required=True)
    registration_date = fields.Date("Date d'enregistrement", required=True)
    original_value = fields.Float("Montant inscrit/couvert ", tracking=True, index=True)
    dispute_case_id = fields.Many2one('collection.dispute.case', string='Dossier', required=True)
    current_value = fields.Float(string="Valeur actuelle", tracking=True, compute="_compute_current_value", store=True)
    first_expiration_date = fields.Date(string="Première date d'expiration", tracking=True, index=True)
    days_to_expiration = fields.Integer(string="Nombre de jours avant expiration", compute="_compute_days_to_expiration", store=True)
    to_renew = fields.Boolean('À renouveler ?', default=False)
    renewal_ids = fields.One2many('collection_disputes_management.collateral_renewal', 'collateral_id', string='Renouvellements')
    reevaluation_ids = fields.One2many('collection_disputes_management.collateral_reevaluation', 'collateral_id', string='Réévaluations')
    state = fields.Selection([
        ('valid', 'Valide'),
        ('expired', 'Expiré'),
    ], string='Statut', default='valid', compute='_compute_state', tracking=True, store=True)

    renewal_count = fields.Integer('Nombre de renouvellements', compute='_compute_counts', store=True)
    reevaluation_count = fields.Integer('Nombre de réévaluations', compute='_compute_counts', store=True)
    current_expiration_date = fields.Date(string="Actuel date d'expiration", tracking=True, compute="_compute_current_expiration_date", store=True)
    guarantor_ids = fields.Many2many('collection_disputes_management.guarantor', 'guarantor_col', string='Garants')
    property_transfer_ids = fields.One2many('collection_disputes_management.property_transfer', 'collateral_id', string="Transfert de propriété")
    is_transferable = fields.Boolean('Est transférable', compute="_compute_is_transferable", store=True)
    constitutive_title_id = fields.Many2one(
        "guarantee.constitutive.title",
        string="Titre constitutif de la garantie",
        required=False,
        help="Exemple : Convention notariée, AMP, Hypothèque..."
    )
    registration_reference = fields.Char("Références d'inscription ou d'opposabilité")
    rank = fields.Selection(
        selection=[(str(i), str(i)) for i in range(1, 11)],
        string="Rang de la garantie",
        help="Ordre de priorité de la garantie (1 = plus prioritaire, 10 = moins prioritaire)."
    )
    duration_months = fields.Integer("Durée de la garantie (en mois)")
    obligee_id = fields.Many2one('res.partner', string="Obligé")

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('collateral.management') or '/'
        return super().create(vals)
    

    @api.depends('current_expiration_date')
    def _compute_days_to_expiration(self):
        for rec in self:
            if rec.current_expiration_date:
                rec.days_to_expiration = (rec.current_expiration_date - date.today()).days
            else:
                rec.days_to_expiration = 0
    
    @api.model
    def cron_update_days_to_expiration(self):
        records = self.search([])
        records._compute_days_to_expiration()
        records._compute_state()

    
    @api.depends('current_expiration_date')
    def _compute_state(self):
        for rec in self:
            if rec.current_expiration_date and rec.current_expiration_date < date.today():
                rec.state = 'expired'
            else:
                rec.state = 'valid'
    

    @api.depends('renewal_ids','reevaluation_ids')
    def _compute_counts(self):
        for rec in self:
            rec.renewal_count = len(rec.renewal_ids)
            rec.reevaluation_count = len(rec.reevaluation_ids)
    
    def action_open_renewals(self):
        return {
            'name': 'Renouvellements',
            'type': 'ir.actions.act_window',
            'res_model': 'collection_disputes_management.collateral_renewal',
            'view_mode': 'list,form',
            'domain': [('collateral_id', '=', self.id)],
            'context': {'default_collateral_id': self.id},
        }

    def action_open_reevaluations(self):
        return {
            'name': 'Réévaluations',
            'type': 'ir.actions.act_window',
            'res_model': 'collection_disputes_management.collateral_reevaluation',
            'view_mode': 'list,form',
            'domain': [('collateral_id', '=', self.id)],
            'context': {'default_collateral_id': self.id},
        }
    
    @api.depends('reevaluation_ids','reevaluation_ids.reevaluation_date', 'reevaluation_ids.new_value', 'original_value')
    def _compute_current_value(self):
        for collateral in self:
            latest_reevaluation = None

            for reevaluation in collateral.reevaluation_ids:
                if not latest_reevaluation or reevaluation.reevaluation_date > latest_reevaluation.reevaluation_date:
                    latest_reevaluation = reevaluation

            if latest_reevaluation:
                collateral.current_value = latest_reevaluation.new_value
            else:
                collateral.current_value = collateral.original_value
    
    @api.depends('registration_date', 'duration_months')
    def _compute_current_expiration_date(self):
        for rec in self:
            if rec.registration_date and rec.duration_months:
                rec.current_expiration_date = rec.registration_date + relativedelta(months=rec.duration_months)
            else:
                rec.current_expiration_date = False
    
    @api.depends('type_id','type_id.is_transferable')
    def _compute_is_transferable(self):
        for collateral in self:
            if collateral.type_id and collateral.type_id.is_transferable == True:
                collateral.is_transferable = True
            else:
                collateral.is_transferable = False