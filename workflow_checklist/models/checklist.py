#-*- coding:utf-8 -*-
from odoo import models, fields, api

class CheckList(models.Model):
    _name = 'workflow_checklist.checklist'
    _description = "Checklist"

    name = fields.Char(string='Nom', required=True)
    section_ids = fields.One2many('workflow_checklist.section', 'checklist_id', string=u"Sections")
    checker_ids = fields.Many2many('res.users', relation='checkers_of_checklist', string=u"Vérificateurs",
        domain=lambda self: [("group_ids", "=", self.env.ref("workflow_checklist.group_user_checker").id)])
    note_decision_ids = fields.One2many('workflow_checklist.checklist_note_decision', 'checklist_id', string=u"Decision sur la note")
