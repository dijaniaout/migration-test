#-*- coding:utf-8 -*-
from odoo import models, fields,api

class ConstitutiveTitle(models.Model):
    _name = "guarantee.constitutive.title"
    _description = "Titre constitutif de garantie"

    name = fields.Char("Libellé", required=True, translate=True)
    code = fields.Char("Code", required=False, help="Code interne si besoin")
    active = fields.Boolean("Actif", default=True)