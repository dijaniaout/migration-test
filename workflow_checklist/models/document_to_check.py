#-*- coding:utf-8 -*-
from odoo import models, fields, api

class DocumentToCheck(models.Model):
    _name = 'workflow_checklist.document_to_check'
    _description = "apply checks on the document"

    step_id = fields.Many2one('customisable_workflow.step', string="Etape", required=True)
    checklist_ids = fields.Many2many('workflow_checklist.checklist', relation='checklist_on_document', string=u"Checklists à appliquer")
    document_id = fields.Many2one('customisable_workflow.document', string=u"Document")
