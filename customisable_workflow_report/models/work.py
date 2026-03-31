# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class Work(models.AbstractModel):
    _inherit = 'customisable_workflow.work'

    document_event_ids = fields.One2many('customisable_workflow_report.work_doc_event', 'res_id',
                                         string="Evènements sur les documents")

    def read(self, fields=None, load='_classic_read'):
        """
            overide to fix document_event_ids not set after work creation
        """
        _logger.info("Context: %r", self.env.context)
        result = super(Work, self).read(fields, load=load)
        for work in result:
            # if doc event is not set, check there is really nothing.
            if not 'document_event_ids' in work or not work['document_event_ids']:
                events = self.env["customisable_workflow_report.work_doc_event"].search([('res_id', '=', work['id']), ('model', '=', self._name)])
                work['document_event_ids'] = [event.id for event in events]
        return result
    
    @api.constrains('current_step_id')
    def _initialize_documents_to_act_on(self):
        for work in self:
            if work.current_step_id:
                work = work.sudo()
                for step_validation in work.current_step_id.document_to_validate_ids:
                    self._all_sources_have_validation_signature_doc_generated(work, step_validation)
                for step_signature in work.current_step_id.document_to_sign_ids:
                    self._all_sources_have_validation_signature_doc_generated(work, step_signature)
                for document in work.current_step_id.generated_document_ids:
                    self._all_documents_have_been_initialized_generated(work, document)
                for document in work.current_step_id.provided_document_ids:
                    self._all_documents_have_been_initialized_generated(work, document)
    
    @api.constrains('current_step_id')
    def _check_previous_step_expected_docs_sates(self):
        for work in self:
            for step_decision in work.previous_step_id.step_decision_ids:
                if work.current_step_id.id == step_decision.target_step_id.id:
                    for expected_document in step_decision.expected_document_state_ids:
                        expected_document.check_work(work)

    @api.constrains('current_step_id')
    def _check_previous_step_all_validations_are_done(self):
        for work in self:
            for step_doc in work.previous_step_id.document_to_validate_ids:
                for existing_doc in work.document_to_validate_ids:
                    if step_doc.document_id.id == existing_doc.origin_id.document_id.id \
                        and existing_doc.step_id.id == work.previous_step_id.id:
                        if not existing_doc.state:
                            raise ValidationError(_("Le document %s doit être traité avant d'avancer dans le processus.", step_doc.document_id.name))

    @api.constrains('current_step_id')
    def _check_previous_step_all_signatures_are_done(self):
        for work in self:
            for step_doc in work.previous_step_id.document_to_sign_ids:
                for existing_doc in work.signed_document_ids:
                    if step_doc.document_id.id == existing_doc.origin_id.document_id.id \
                        and existing_doc.step_id.id == work.previous_step_id.id:
                        if not existing_doc.state:
                            raise ValidationError(_("Le document %s doit être traité avant d'avancer dans le processus.", step_doc.document_id.name))    
    
    def _all_sources_have_validation_signature_doc_generated(self, work, step_action):
        source_documents = self.env['customisable_workflow_report.work_doc_event'].sudo().search_read([
                                                ('model', '=', work._name),('res_id', '=', work.id),
                                                ('document_model', 'in', ('customisable_workflow.work_generated_document', 
                                                                          'customisable_workflow.work_given_document')),
                                                ('document_id', '=', step_action.document_id.id)])
        if not source_documents:
            raise ValidationError(_("Attention, le document %s devant être traité ne semble pas être là. Veuillez contacter l'administrateur.",
                                    step_action.document_id.name))
        for source_document in source_documents:
            # check document has not yet been created for that step
            has_been_created, last_event = self._get_has_been_created_or_get_last_event(work, source_document)
            if not has_been_created:
                if last_event['type'] == 'creation' or (last_event['state'] and last_event['state'] != 'rejected'):
                    if step_action._name == 'customisable_workflow_validation.step.validation':
                        vals = {
                            'model': self._name,
                            'res_id': work.id,
                            'origin_id': step_action.id,
                            'step_id': work.current_step_id.id,
                            'parent_id': last_event['reference'],
                            'parent_model': last_event['document_model'],
                        }
                        action_model = "customisable_workflow_validation.work_doc_to_validate"
                    else:
                        last_signature_type = False
                        if last_event['document_model'] == 'customisable_workflow_validation.work_doc_to_validate':
                            last_document = self.env['customisable_workflow_report.work_doc_event'].sudo().search([('model', '=', work._name),('res_id', '=', work.id),
                                            ('document_id', '=', step_action.document_id.id),('document_model', '=', 'customisable_workflow_signature.work_signed_document')], 
                                            order='reference DESC', limit=1)  
                            if last_document: 
                                last_signature_type = last_document.signature_type                                                           
                        else:
                            last_signature_type = last_event['signature_type']
                        vals = {
                            'model': work._name,
                            'res_id': work.id,
                            'origin_id': step_action.id,
                            'step_id': work.current_step_id.id,
                            'parent_id': last_event['reference'],
                            'parent_model': last_event['document_model'],
                            'signature_type': last_signature_type
                        }
                        action_model = "customisable_workflow_signature.work_signed_document"
                    action_document = self.env[action_model].sudo().create(vals)
                    source_result_fields = ('result_document', 'result_document_pdf')
                    if last_event['type'] == 'creation':
                        source_result_fields = ('attachment', 'attachment_pdf')
                    result_attachments = self.env['ir.attachment'].sudo().search([
                        ('res_model', '=', last_event['document_model']),
                        ('res_field', 'in',source_result_fields),
                        ('res_id', '=', last_event['reference'])])
                    for result_attachment in result_attachments:
                        result_attachment.copy({'res_model': action_model,'res_id': action_document.id,
                                                'res_field': result_attachment.res_field.replace('result', 'source').replace('attachment', 'source_document')})
    
    def _get_has_been_created_or_get_last_event(self, work, source_document):
        last_event  = source_document
        while True:
            event = self.env['customisable_workflow_report.work_doc_event'].sudo().search_read([
                                                ('model', '=', last_event['model']),('res_id', '=', last_event['res_id']),
                                                ('parent_model', '=', last_event['document_model']),
                                                ('parent_id', '=', last_event['reference']),
                                                ('document_id', '=', last_event['document_id'][0])], limit=1)
            if event:
                if event[0]['step_id'][0] == work.current_step_id.id:
                    return (True, None)
                last_event = event[0]
            else:
                break
        return (False, last_event)
    
    def _all_documents_have_been_initialized_generated(self, work, document):
        source_documents = self.env['customisable_workflow_report.work_doc_event'].sudo().search_read([
                                                ('model', '=', work._name),('res_id', '=', work.id),
                                                ('document_model', 'in', ('customisable_workflow.work_generated_document', 
                                                                          'customisable_workflow.work_given_document')),
                                                ('document_id', '=', document.id)], limit=1, order='reference DESC')
        generate = not source_documents
        for source_document in source_documents:
            _has_been_created, last_event = self._get_has_been_created_or_get_last_event(work, source_document)
            if not _has_been_created and (last_event['state'] and last_event['state'] == 'rejected'):
                generate = True
                break
        if generate:
            if document.source == 'generated':
                self.sudo()._prepare_doc_to_generate(work, document)
            elif document.source == 'provided':
                self.sudo()._prepare_doc_to_provide(work, document)

    def _prepare_doc_to_generate(self, work, document):
        if document.document:
            report = self.env['ir.actions.report'].sudo().search([('report_name', '=', 'work.docx')], limit=1)
            result = report.sudo().render_pdf_and_docx([work.sudo()], data={'template':document.sudo()})
            if document.document_format_to_generate == 'pdf':
                template_name = document.name + '.pdf'
                attachment = base64.b64encode(result['pdf'][0])
                attachment_pdf = False
            else:
                template_name = document.name + '.docx'
                attachment = base64.b64encode(result['docx'][0])
                attachment_pdf = base64.b64encode(result['pdf'][0])
        else:
            result, format = document.report_id._render_qweb_pdf(document.report_id.id, res_ids=[work.id])
            if document.document_format_to_generate == 'pdf':
                template_name = document.name + '.pdf'
                attachment = base64.b64encode(result)
                attachment_pdf = False
        generated_document = self.env['customisable_workflow.work_generated_document'].sudo().create({'model': self._name,
                                                                        'res_id': work.id,
                                                                        'name': document.name,
                                                                        'step_id':  work.current_step_id.id,
                                                                        'document_id': document.id})
        self.env['ir.attachment'].create({
            'name': template_name,
            'datas': attachment,
            'res_model': 'customisable_workflow.work_generated_document',
            'res_id': generated_document.id,
            'res_field': 'attachment',
            'public': True
        })
        if attachment_pdf:
            self.env['ir.attachment'].create({
                'name': document.name + '.pdf',
                'datas': attachment_pdf,
                'res_model': 'customisable_workflow.work_generated_document',
                'res_id': generated_document.id,
                'res_field': 'attachment_pdf',
                'public': True
            })
    
    def _prepare_doc_to_provide(self, work, document):
        vals = {
            'model': self._name,
            'res_id': work.id,
            'step_id':  work.current_step_id.id,
            'document_id': document.id
        }
        self.env["customisable_workflow.work_given_document"].sudo().create(vals)