#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
import base64
import logging
_logger = logging.getLogger(__name__)

class StepSignature(models.Model):
    _name = 'customisable_workflow_signature.step.signature'
    _description = "Step signature"

    step_id = fields.Many2one('customisable_workflow.step', string="Etape", required=True, ondelete='cascade')
    document_id = fields.Many2one('customisable_workflow.document', string="Document", required=True)
    allowed_group_ids = fields.Many2many('res.groups', string="Groupes autorisés")
    
