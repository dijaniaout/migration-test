#-*- coding:utf-8 -*-
import os
import uuid
import base64
import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)
class WorkGivenDocument(models.Model):
    _name = 'customisable_workflow.work_given_document'
    _order = "res_id, id desc"
    _description = "Work given document"

    model = fields.Char('Related Document Model', index=True)
    res_id = fields.Many2oneReference('Related Document ID', index=True, model_field='model')
    step_id = fields.Many2one('customisable_workflow.step', string="Etape", required=True, ondelete='cascade')
    document_id = fields.Many2one('customisable_workflow.document', string=u"Document demandé", required=True, ondelete='cascade')
    name = fields.Char(related="document_id.name", string='Nom')
    document_type_id = fields.Many2one(related="document_id.document_type_id", string="Type de document")
    is_required = fields.Boolean(related="document_id.is_required", string="Est obligatoire?")
    attachment = fields.Binary('Document', attachment=True)
    # In case the attachement is in docx, save a pdf version.
    attachment_pdf = fields.Binary('Document pdf', attachment=True)

    def create_pdf_from_docx(self):
        attachment = self.env['ir.attachment'].search([('res_model', '=', 'customisable_workflow.work_given_document'), ('res_field', '=', 'attachment'),
                                                        ('res_id', '=', self.id)])
        docx_path = attachment._full_path(attachment.store_fname)
        file_name = os.path.basename(docx_path)
        _logger.error(file_name)
        cmd = "soffice --headless --convert-to pdf --outdir /tmp " + docx_path
        os.system(cmd)
        f = open('/tmp/' + file_name + '.pdf', "rb")
        pdf = f.read()
        f.close()
        self.env['ir.attachment'].create({
                                'name': self.name + '.pdf',
                                'datas': base64.b64encode(pdf),
                                'res_model': 'customisable_workflow.work_given_document',
                                'res_id': self.id,
                                'res_field': 'attachment_pdf',
                                'public': True
                            })
        