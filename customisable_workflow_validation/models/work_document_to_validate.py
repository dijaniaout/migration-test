#-*- coding:utf-8 -*-
from odoo import models, fields, _
import base64
import logging

_logger = logging.getLogger(__name__)

class WorkDocumentToValidate(models.Model):
    _name = 'customisable_workflow_validation.work_doc_to_validate'
    _inherit = ['customisable_workflow.work_document_action']
    _order = "res_id, id desc"
    _description = "Work validated document"

    origin_id = fields.Many2one('customisable_workflow_validation.step.validation', string="Origine", required=True)
    source_name = fields.Char(related="origin_id.document_id.name", string='Nom')
    state = fields.Selection([('validated', "Validé"),('rejected', "Rejeté")], string='État')
    source_image = fields.Image('Document à valider (Image)', compute='_compute_source')
    source_text = fields.Text('Document à valider (Texte)', compute='_compute_source')
    source_pdf = fields.Binary('Document à valider (PDF)', compute='_compute_source')
    
    def _compute_source(self):
        for record in self:
            record.source_pdf = False
            record.source_image = False
            record.source_text = False
            if record.source_document_pdf:
                record.source_pdf = record.source_document_pdf
            else:
                attachement = self.env['ir.attachment'].search([('res_model', '=', 'customisable_workflow_validation.work_doc_to_validate'), 
                                                    ('res_field', '=', 'source_document'),('res_id', '=', record.id)])
                if attachement:
                    if attachement.mimetype == 'application/pdf':
                        record.source_pdf = record.source_document
                    elif 'image' in attachement.mimetype:
                        record.source_image = record.source_document
                    elif 'text' in attachement.mimetype:
                        record.source_text = base64.decodebytes(record.source_document)

    def validate(self):
        """
        Validate action
        """
        self.write({'actor_user_id':self.env.user.id,
                    'state': 'validated',
                    'action_date': fields.Datetime.now()
                  })
        source_attachments = self.env['ir.attachment'].sudo().search([
             ('res_model', '=', self._name),
             ('res_field', 'in', ('source_document', 'source_document_pdf')),
             ('res_id', '=', self.id)])
        for source_attachment in source_attachments:
            source_attachment.copy({'res_field': source_attachment.res_field.replace('source', 'result')})