#-*- coding:utf-8 -*-
from odoo import models, fields, api

class Section(models.Model):
    _name = 'workflow_checklist.section'
    _description = "section"

    name = fields.Char(string='Nom', required=True)
    parent_id = fields.Many2one('workflow_checklist.section',string='Parent')
    check_ids = fields.One2many('workflow_checklist.check', 'section_id', string=u"Checks")
    checklist_id = fields.Many2one('workflow_checklist.checklist', string=u"check list", required=True, ondelete="cascade")
