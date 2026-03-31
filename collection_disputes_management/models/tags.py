#-*- coding:utf-8 -*-
from odoo import models, fields, api,  _
import logging

_logger = logging.getLogger(__name__)

class Tags(models.Model):
    _name = 'collection_disputes_management.tag'
    _description = 'Etiquette'
    _order = 'create_date desc'

    name = fields.Char(string='Nom de l\'étiquette', required=True)