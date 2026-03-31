#-*- coding:utf-8 -*-
from odoo import models, fields, api, _

class Step(models.Model):
    _inherit = 'customisable_workflow.step'
    _description = "step"

    document_to_check_ids = fields.One2many('workflow_checklist.document_to_check', 'step_id', string=u"Données à vérifier")
    