#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from lxml import etree
import logging

_logger = logging.getLogger(__name__)

class WorkDemo(models.Model):
    _name = 'customisable_workflow_demo.work_demo'
    _inherit = ['customisable_workflow.work']
    _description = "Work demo"
    _order = "id desc"

    description = fields.Text()