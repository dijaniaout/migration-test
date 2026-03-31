#-*- coding:utf-8 -*-
from odoo import models, fields, api, _

class TransitionRule(models.Model):
    _name = 'customisable_workflow.transition_rule'
    _description = 'Transition Rule'

    name = fields.Char(string='Nom', required=True)
    condition_ids = fields.One2many('customisable_workflow.condition', 'transition_rule_id', string=u"Conditions")
    delay_before_automatic_transition = fields.Integer(string=u"Délai avant la transition automatique")
    cumulative_mode = fields.Boolean(string="Mode cumulatif?", default=True, required=True)
    