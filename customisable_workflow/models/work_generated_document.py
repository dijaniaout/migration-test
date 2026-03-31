#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class WorkGeneratedDocument(models.Model):
    _name = 'customisable_workflow.work_generated_document'
    _order = "res_id, id desc"
    _description = "Work generated document"

    name = fields.Char(string='Nom')
    model = fields.Char('Related Document Model', index=True, required=True)
    res_id = fields.Many2oneReference('Related Document ID', index=True, model_field='model', required=True)
    step_id = fields.Many2one('customisable_workflow.step', string="Etape", ondelete='cascade', required=True)
    document_id = fields.Many2one('customisable_workflow.document', string="Document à générer", 
                                  required=True, ondelete='cascade', domain="[('source','=','generated')]")
    format = fields.Selection(string="Format", related="document_id.document_format_to_generate")
    attachment = fields.Binary('Document', attachment=True , required=True)
    # In case the attachement is in docx, save a pdf version.
    attachment_pdf = fields.Binary('Document pdf', attachment=True , required=True)
