#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class StepValidation(models.Model):
    _name = 'customisable_workflow_validation.step.validation'
    _description = "Step validation"

    step_id = fields.Many2one('customisable_workflow.step', string="Etape", required=True)
    document_id = fields.Many2one('customisable_workflow.document', string="Document", required=True)
    allowed_group_ids = fields.Many2many('res.groups', string="Groupes autorisés")
    
