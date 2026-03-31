#-*- coding:utf-8 -*-
from odoo import models, fields, api, _

class Municipality(models.Model):
    _name = 'sn_administrative_division.municipality'
    _order = "name asc"
    _description = "Commune"
    
    name = fields.Char(string=u'Nom', required=True)
    department_id = fields.Many2one('sn_administrative_division.department',string=u'Département', required=True)