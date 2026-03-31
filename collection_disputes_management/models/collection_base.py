#-*- coding:utf-8 -*-
from odoo import models, fields, api,  _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class CollectionBase(models.AbstractModel):
    _name = 'collection.case.base'
    _inherit = ['customisable_workflow.work','mail.thread','mail.activity.mixin']
    _description = "Base Model"
    
    base_workflow_id = fields.Many2one('customisable_workflow.workflow', string='Processus de base')