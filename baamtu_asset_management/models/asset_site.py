from odoo import models, fields, api

class AssetSite(models.Model):
    _name = 'asset.site'
    _description = 'Site'
    _rec_name = 'name'

    name = fields.Char(string="Nom du site", required=True)
    code = fields.Char(string="Code", required=True)
    company_id = fields.Many2one('res.company', string="Société", required=True, default=lambda self: self.env.company) 
    floor_ids = fields.One2many('asset.floor', 'site_id', string="Étages",)
    latitude = fields.Float(string="Latitude")
    longitude = fields.Float(string="Longitude")
    asset_ids = fields.One2many('account.asset', 'site_id', string="Immobilisations")
    asset_count = fields.Integer(
        string="Assets",
        compute="_compute_asset_count"
    )

    @api.depends('asset_ids')
    def _compute_asset_count(self):
        for record in self:
            record.asset_count = len(record.asset_ids)

    def action_view_assets(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Immobilisations du site",
            "res_model": "account.asset",
            "view_mode": "list,form",
            "domain": [("site_id", "=", self.id)],
        }
        
    _code_unique = models.Constraint(
        'unique(code)',
        'Le code du site doit être unique.'
    )