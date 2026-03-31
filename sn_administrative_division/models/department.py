#-*- coding:utf-8 -*-
from odoo import models, fields, api, _

class Department(models.Model):
    _name = 'sn_administrative_division.department'
    _order = "name asc"
    _description = "Département"
    
    name = fields.Char(string=u'Nom', required=True)
    region_id = fields.Many2one('sn_administrative_division.region', string=u'Région', required=True)
    municipality_ids = fields.One2many('sn_administrative_division.municipality', 'department_id', string='Départements')