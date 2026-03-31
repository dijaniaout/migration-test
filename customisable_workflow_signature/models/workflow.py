#-*- coding:utf-8 -*-
from odoo import models, fields, api, _

class Workflow(models.Model):
    _inherit = 'customisable_workflow.workflow'

    has_documents_to_sign = fields.Boolean(string="A un document à signer", compute="_compute_has_documents_to_sign")
    electronic_signature = fields.Boolean(string=u'Signature électronique', default=True)
    manual_signature = fields.Boolean(string='Signature manuelle', default=False)

    def _compute_has_documents_to_sign(self):
        for workflow in self:
            workflow.has_documents_to_sign = any(step.document_to_sign_ids for step in workflow.step_ids)