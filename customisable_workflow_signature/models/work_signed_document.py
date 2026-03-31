#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import os
import uuid
import logging

_logger = logging.getLogger(__name__)

class WorkSignedDocument(models.Model):
    _name = 'customisable_workflow_signature.work_signed_document'
    _inherit = ['customisable_workflow.work_document_action']
    _description = "Work signed document"

    origin_id = fields.Many2one('customisable_workflow_signature.step.signature', string="Origine", required=True)
    source_name = fields.Char(related="origin_id.document_id.name", string='Nom')
    state = fields.Selection([('signed', "Signé"),('rejected', "Rejeté")], string='État')
    signature = fields.Image(string="Image", max_width=100)
    signature_type = fields.Selection([('manual', "Manuelle"),('electronic', "Electronique")], string='Type de signature')
    electronic_signature = fields.Boolean(related="origin_id.step_id.workflow_id.electronic_signature")
    manual_signature = fields.Boolean(related="origin_id.step_id.workflow_id.manual_signature")
    
    @api.depends('result_document')
    def _compute_signed(self):
        for record in self:
            if record.result_document:
                record.state = 'signed'
    
    def sign(self):
        """
        Sign action
        """
        signature_attachment = self.env['ir.attachment'].sudo().search([('res_model', '=', 'res.partner'),('res_field', '=', 'document_signature'),('res_id', '=', self.env.user.partner_id.id)])
        if not signature_attachment:
            raise UserError("Veuillez mettre votre signature sur votre profil.")
        signature_path = signature_attachment._full_path(signature_attachment.store_fname)
        self._sign(signature_path)
    
    def sign_with_signature(self, signature):
        """
        Sign wih the given signature
        """
        self.signature = signature
        signature_attachment = self.env['ir.attachment'].sudo().search([('res_model', '=', 'customisable_workflow_signature.work_signed_document'),
            ('res_field', '=', 'signature'),('res_id', '=', self.id)])
        signature_path = signature_attachment._full_path(signature_attachment.store_fname)
        self._sign(signature_path)
        
    
    def _sign(self, signature_path):
        report = self.env['ir.actions.report'].sudo().search([('report_name', '=', 'work.docx')], limit=1)
        result = report.sudo().add_signature_to_report(base64.b64decode(self.source_document), signature_path)
        attachment = base64.b64encode(result['pdf'][0])
        attachment_docx = base64.b64encode(result['docx'][0])
        self.write({'actor_user_id': self.env.user.id,
                    'action_date': fields.Datetime.now(),
                    'state': 'signed',
                    'signature_type': 'electronic',
                  })
        self.env['ir.attachment'].sudo().create({
                                'name': self.source_name + '.pdf',
                                'datas': attachment,
                                'res_model': self._name,
                                'res_id': self.id,
                                'res_field': 'result_document_pdf',
                                'public': True
                            })
        self.env['ir.attachment'].sudo().create({
                                'name': self.source_name + '.docx',
                                'datas': attachment_docx,
                                'res_model': self._name,
                                'res_id': self.id,
                                'res_field': 'result_document',
                                'public': True
                            })
