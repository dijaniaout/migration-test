#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WorkTest(models.Model):
    _name = 'customisable_workflow.work_test'
    _inherit = ['customisable_workflow.work']
    _description = "Work test"
    _order = "id desc"

    state = fields.Selection(selection_add=[
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),   
     ], string='Etat', default='draft')


    def action_confirm(self):
        self.write({'state': 'confirmed'})