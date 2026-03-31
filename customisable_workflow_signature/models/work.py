# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class Work(models.AbstractModel):
    _inherit = 'customisable_workflow.work'

    signed_document_ids = fields.One2many('customisable_workflow_signature.work_signed_document', 'res_id', string=u"Documents signés")
    has_documents_to_sign = fields.Boolean(string="A un document à signer", related="workflow_id.has_documents_to_sign")

    @api.constrains('current_step_id')
    def _check_previous_step_docs_to_sign(self):
        for work in self:
            if work.previous_step_id:
                for step_signature in work.previous_step_id.document_to_sign_ids:
                    doc_to_sign_is_there = False
                    for existing_doc in work.signed_document_ids:
                        if step_signature.document_id.id == existing_doc.origin_id.document_id.id and existing_doc.step_id.id == work.previous_step_id.id:
                            doc_to_sign_is_there = True
                    if not doc_to_sign_is_there:
                        raise ValidationError(_("Le document %s devant être signé n'est pas disponible. Veuillez contacter l'équipe technique.", step_signature.document_id.name))

