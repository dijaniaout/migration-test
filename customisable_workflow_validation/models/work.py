# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class Work(models.AbstractModel):
    _inherit = 'customisable_workflow.work'

    document_to_validate_ids = fields.One2many('customisable_workflow_validation.work_doc_to_validate', 'res_id', string=u"Documents à valider")
    has_documents_to_validate = fields.Boolean(string="A un document à valider", related="workflow_id.has_documents_to_validate")

    @api.constrains('current_step_id')
    def _check_previous_step_docs_to_validate(self):
        for work in self:
            if work.previous_step_id:
                for step_validation in work.previous_step_id.document_to_validate_ids:
                    doc_to_validate_is_there = False
                    for existing_doc in work.document_to_validate_ids:
                        if step_validation.document_id.id == existing_doc.origin_id.document_id.id and existing_doc.step_id.id == work.previous_step_id.id:
                            doc_to_validate_is_there = True
                    if not doc_to_validate_is_there:
                        raise ValidationError(_("Le document %s devant être validé n'est pas disponible. Veuillez contacter l'équipe technique.", step_validation.document_id.name))
    
    
