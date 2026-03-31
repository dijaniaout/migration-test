#-*- coding:utf-8 -*-
from odoo import models, fields, api, _

class Workflow(models.Model):
    _inherit = 'customisable_workflow.workflow'

    has_document_to_check = fields.Boolean(string="A un document à vérifer", compute="_compute_has_document_to_check")

    def _compute_has_document_to_check(self):
        for workflow in self:
            workflow.has_document_to_check = any(step.document_to_check_ids for step in workflow.step_ids)