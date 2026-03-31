#-*- coding:utf-8 -*-
from odoo import models, fields, api

class Check(models.Model):
    _name = 'workflow_checklist.check'
    _description = "Check"

    name = fields.Char(string='Nom', required=True)
    maximum_number_of_points = fields.Float(required=True, string="Nombre maximum de points")
    section_id = fields.Many2one('workflow_checklist.section', string=u"Section", required=True, ondelete="cascade")
    type_response = fields.Selection([('note', "Note"),('yes_or_no', "Oui/Non"),('multiple_choices', "Choix multiples"),('fields', "Champ")],required=True, string="Type de réponse ", default= 'note')
    choice_ids = fields.One2many('workflow_checklist.ckeck.multiple_choice', 'check_id', string='Choix possibles')
    field_id = fields.Many2one(
        'ir.model.fields', domain=[('model_id.model', '=', 'customisable_workflow.work'),('readonly', '=', False),('ttype', '!=', 'many2many'),('ttype', '!=', 'one2many')],
        ondelete='cascade', string="Information sur dossier")
