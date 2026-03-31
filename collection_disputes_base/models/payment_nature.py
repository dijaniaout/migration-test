#-*- coding:utf-8 -*-
from odoo import models, fields, api,  _

class PaymentNature(models.Model):
    _name = 'payment.nature'
    _description = "Nature du Paiement"

    name = fields.Char(string="Nom", required=True)
