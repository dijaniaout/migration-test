# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResUsers(models.Model):
    _inherit = 'res.users'

    responsibility_transfer_ids = fields.One2many("customisable_workflow.responsibility_transfer", 'delegate_id', string=u'Transferts de responsabilité')