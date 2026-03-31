# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResponsibilityTransfer(models.Model):
    _name = 'customisable_workflow.responsibility_transfer'
    _description = 'Transfert de responsabilité'

    start_date = fields.Date(string=u"Date de début", required=True)
    end_date = fields.Date(string="Date de fin", required=True)
    delegate_responsibility_id = fields.Many2one("res.users", string=u'Délégué', required=True)
    delegate_id = fields.Many2one("res.users", string=u'Délégant', ondelete='restrict', required=True)
    interim_note = fields.Binary(string="Note d'intérim", required=True)
    interim_note_filename = fields.Char(string='Nom du document')