# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    document_signature = fields.Image("Signature des documents", max_width=200)