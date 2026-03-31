from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    entity_code = fields.Char(string='Code entité')
    
    _unique_entity_code = models.Constraint(
        'unique(entity_code)',
        'Le code entité doit être unique.',
    )