# -*- coding:utf-8 -*-
from odoo import api, fields, models, exceptions,_
from odoo.exceptions import ValidationError

class ExpectedDocumentState(models.Model):
    _name = "customisable_workflow.expected_document_state"
    _description = "État attendu du document"

    step_decision_id = fields.Many2one('customisable_workflow.step_decision', string=u"Décision", required=True, ondelete='cascade')
    document_id = fields.Many2one('customisable_workflow.document', string=u"Document", required=True, readonly=True)
    expected_state = fields.Selection([('signed', u"Signé"),('validated', u"Validé"),('rejected', u"Rejeté")], string='État attendu')
    concerned_action = fields.Selection([('signature', u"Signature"),('validation', u"Validation")], string=u'Action concernée', required=True, readonly=True)

    def check_work(self,work):
        for record in self:
            document_model = ''
            if record.concerned_action == "validation":
                document_model = 'customisable_workflow_validation.work_doc_to_validate'
            if record.concerned_action == "signature":
                document_model = 'customisable_workflow_signature.work_signed_document'
            record._check_if_state_is_respected(document_model, work)
                  
    def _check_if_state_is_respected(self, document_model, work):
        for record in self:
            concerned_document = self.env['customisable_workflow_report.work_doc_event'].sudo().search([('model', '=', work._name),('res_id', '=', work.id),
                                                                                                    ('document_id', '=', record.document_id.id),('step_id', '=', work.previous_step_id.id),
                                                                                                    ('document_model', '=', document_model)], order='reference DESC', limit=1)
            if record.expected_state and concerned_document:
                if record.expected_state == 'validated':
                    expected_state = 'valide'
                if record.expected_state == 'signed':
                    expected_state = 'signé'
                if record.expected_state == 'rejected':
                    expected_state = 'rejeté'
                if concerned_document.state != record.expected_state:
                    raise ValidationError(_("Le document %s doit être %s avant d'aller à cette étape.", concerned_document.group_name,expected_state))