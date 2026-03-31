#-*- coding:utf-8 -*-
from odoo import models, fields, api, _

class Workflow(models.Model):
    _inherit = 'customisable_workflow.workflow'

    has_documents_to_validate = fields.Boolean(string="A un document à valider", compute="_compute_has_documents_to_validate")

    def _compute_has_documents_to_validate(self):
        for workflow in self:
            workflow.has_documents_to_validate = any(step.document_to_validate_ids for step in workflow.step_ids)