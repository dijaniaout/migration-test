#-*- coding:utf-8 -*-
from odoo import models, fields, api,  _
import logging

_logger = logging.getLogger(__name__)

class InterventionType(models.Model):
    _name = 'collection_disputes_management.intervention_type'
    _description = "Type d'intervention"
    _order = 'create_date desc'

    name = fields.Char(string='Type de l\'intervention', required=True)