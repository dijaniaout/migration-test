from odoo import models, fields

class AssetFloor(models.Model):
    _name = 'asset.floor'
    _description = 'Etage'
    _rec_name = 'name'

    name = fields.Char(string="Nom de l\'étage", required=True)
    code = fields.Char(string="Code")
    site_id = fields.Many2one('asset.site', string="Site", required=True, ondelete='cascade')

    _floor_unique_per_site = models.Constraint(
        'unique(code, site_id)',
        'Le code étage doit être unique par site.'
    )
