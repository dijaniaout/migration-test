
#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Step(models.Model):
    _inherit = 'customisable_workflow.step'

    document_to_validate_ids = fields.One2many('customisable_workflow_validation.step.validation', 'step_id', string=u"Documents à valider")

    @api.constrains('document_to_validate_ids')
    def _check_documents_to_validate_are_already_chosen(self):
        for step in self:
            if step.document_to_validate_ids:
                for document_to_validate in step.document_to_validate_ids:
                    documents_to_validate = self.env['customisable_workflow_validation.step.validation'].sudo().search([('document_id', '=', document_to_validate.document_id.id),('step_id', '=', step.id)])
                    if len(documents_to_validate) >= 2:
                        raise ValidationError(_("Le document %s est déja choisi pour validation.", document_to_validate.document_id.name))
    
    @api.constrains('document_to_validate_ids','step_decision_ids')
    def _check_expected_documents_state_for_validation(self):
        for step in self:
            if step.document_to_validate_ids:
                for document_to_validate in step.document_to_validate_ids:
                    if step.step_decision_ids:
                        for step_decision in step.step_decision_ids:
                            document_is_there = self.env['customisable_workflow.expected_document_state'].search([('step_decision_id', '=', step_decision.id),
                                                                                                                ('document_id', '=', document_to_validate.document_id.id),
                                                                                                                ('concerned_action', '=', 'validation')])
                            if not document_is_there:
                                self.env['customisable_workflow.expected_document_state'].create({
                                                'document_id': document_to_validate.document_id.id,
                                                'step_decision_id': step_decision.id,
                                                'concerned_action': 'validation',
                                            })
    
    @api.constrains('document_to_validate_ids','step_decision_ids')
    def _check_unlink_expected_documents_state_for_validation(self):
        for step in self:
            if step.step_decision_ids:
                for step_decision in step.step_decision_ids:
                    if step_decision.expected_document_state_ids:
                        for expected_document in step_decision.expected_document_state_ids:
                            if expected_document.concerned_action and expected_document.concerned_action == 'validation':
                                if expected_document.document_id.id:
                                    document_to_validate_is_there = False
                                    if step.document_to_validate_ids:
                                        for document_to_validate in step.document_to_validate_ids:
                                            if document_to_validate.document_id.id == expected_document.document_id.id:
                                                document_to_validate_is_there = True
                                                break
                                    if not document_to_validate_is_there:
                                        expected_document.unlink()