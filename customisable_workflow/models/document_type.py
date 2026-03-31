#-*- coding:utf-8 -*-
from odoo import models, fields, api, _

class DocumentType(models.Model):
    _name = 'customisable_workflow.document_type'
    _order = "name asc"
    _description = "Type de document"
    
    name = fields.Char(string='Nom', required=True)