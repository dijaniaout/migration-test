#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)
class Work(models.AbstractModel):
    _inherit = 'customisable_workflow.work'

    checklist_response_ids = fields.One2many('workflow_checklist.checklist_response', 'res_id', string=u'liste des reponses')
    has_document_to_check = fields.Boolean(string="A un document à vérifer", related="workflow_id.has_document_to_check")

    @api.constrains('current_step_id')
    def _get_checklist_response(self):
        for work in self:
            for document in work.current_step_id.document_to_check_ids:
                for checklist in document.checklist_ids:
                    checklist_response = self.env['workflow_checklist.checklist_response'].create({
                            'model': self._name,
                            'res_id': work.id,
                            'document_id': document.document_id.id,
                            'checklist_id': checklist.id,
                            'step_id': work.current_step_id.id,
                            'checker_ids': checklist.checker_ids
                        })
                    for section in checklist.section_ids:
                        for check in section.check_ids:
                            self.env['workflow_checklist.check_response'].create({
                                'check_id': check.id,
                                'checklist_response_id':checklist_response.id
                            })