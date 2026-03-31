#-*- coding:utf-8 -*-
from odoo import models, fields, api, _

class Region(models.Model):
    _name = 'sn_administrative_division.region'
    _order = "name asc"
    _description = "Région"
    
    name = fields.Char(string=u'Nom', required=True)
    department_ids = fields.One2many('sn_administrative_division.department', 'region_id', string='Départements')