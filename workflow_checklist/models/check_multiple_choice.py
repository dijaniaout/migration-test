from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class MultipleChoice(models.Model):
    _name = 'workflow_checklist.ckeck.multiple_choice'
    _rec_name = 'value'
    _order = 'sequence, id'
    _description = 'Multiple Choice'

    check_id  = fields.Many2one('workflow_checklist.check', string='Check', required=True, ondelete="cascade")
    sequence = fields.Integer(u'Séquence', default=10)
    value = fields.Char('Choix', required=True)