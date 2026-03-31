#-*- coding:utf-8 -*-
from odoo import models, fields, tools, api

class DunningRule(models.Model):
    _inherit = 'customisable_workflow.dunning.rule'
    _description = "Règle de relance"

    field_id = fields.Many2one('ir.model.fields', domain="[('model_id.model', '=', 'collection.dispute.case'), '|', ('ttype', '=', 'float'), ('ttype', '=', 'integer')]", string=u"Champ", required=True, ondelete='cascade')