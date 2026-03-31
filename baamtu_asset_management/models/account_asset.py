from odoo import fields, models, api
from odoo.exceptions import UserError
import qrcode
import base64
from io import BytesIO
class AccountAsset(models.Model):
    _inherit = 'account.asset'
    
    country_code = fields.Char(string="Pays", related="company_id.country_code", store=True, readonly=True)
    entity_code = fields.Char(string="Entité", related="company_id.entity_code", store=True, readonly=True)
    site_id = fields.Many2one('asset.site', string="Site")
    floor_id = fields.Many2one('asset.floor', string="Étage", domain="[('site_id', '=', site_id)]")
    imo_code = fields.Char(string="Code IMO", readonly=True, copy=False, index=True,)
    code = fields.Char(string="Code ", readonly=True, copy=False, index=True,)
    employee_id = fields.Many2one('hr.employee', compute='_compute_asset_assign',
        store=True, readonly=False, string='Employé', tracking=True, index='btree_not_null')
    department_id = fields.Many2one('hr.department', compute='_compute_asset_assign',
        store=True, readonly=False, string='Département', tracking=True)
    asset_assign_to = fields.Selection(
        [('department', 'Département'), ('employee', 'Employé'), ('other', 'Autre')],
        string='Utilisé par',
        required=True,
        default='employee')
    assign_date = fields.Date(compute='_compute_asset_assign', store=True, readonly=False, copy=True)
    qr_code = fields.Binary("QR Code", compute="_compute_qr_code", store=True)

    @api.depends('imo_code')
    def _compute_qr_code(self):
        for rec in self:
            if rec.imo_code:
                qr = qrcode.make(rec.imo_code)
                buffer = BytesIO()
                qr.save(buffer, format="PNG")
                rec.qr_code = base64.b64encode(buffer.getvalue())
            else:
                rec.qr_code = False


    _imo_code_uniq = models.Constraint(
        'unique(imo_code)',
        'Le code IMO doit être unique.',
    )
    
    @api.depends('asset_assign_to')
    def _compute_asset_assign(self):
        for asset in self:
            if asset.asset_assign_to == 'employee':
                asset.department_id = False
                asset.employee_id = asset.employee_id
            elif asset.asset_assign_to == 'department':
                asset.employee_id = False
                asset.department_id = asset.department_id
            else:
                asset.department_id = asset.department_id
                asset.employee_id = asset.employee_id
            asset.assign_date = fields.Date.context_today(self)
    
    @api.model
    def create(self, vals):
        record = super().create(vals)
        if not record.imo_code:
            record._generate_imo_code()
        return record

    def action_generate_imo_code(self):
        for rec in self:
            if rec.imo_code:
                raise UserError("Le code IMO est déjà généré.")

            if not (rec.country_code and rec.entity_code and rec.site_id and rec.floor_id and rec.model_id):
                raise UserError(
                    "Veuillez renseigner Pays, Entité, Site, Étage et Modèle d'immobilisation avant de générer le code IMO."
                )

            rec._generate_imo_code()
            rec._compute_qr_code()
   
    def _generate_imo_code(self):
        for rec in self:
            if not rec.company_id:
                continue

            sequence = self.env['ir.sequence'].next_by_code(
                'asset.imo.sequence'
            ) or '0000'

            country = rec.country_code or ''
            entity = rec.entity_code or ''
            site = rec.site_id.code or ''
            floor = rec.floor_id.code or ''
            asset_type = rec.model_id.code or ''

            rec.imo_code = f"{country}-{entity}-{site}-{floor}-{asset_type}-{sequence}"
