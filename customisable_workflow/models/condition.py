#-*- coding:utf-8 -*-
from odoo import models, fields, api, exceptions,_

import logging
_logger = logging.getLogger(__name__)
class Condition(models.Model):
    _name = 'customisable_workflow.condition'
    _description = 'Condition'

    res_model_id = fields.Many2one('ir.model', string=u'Modèle', ondelete='cascade', required=True)
    field_id = fields.Many2one('ir.model.fields', ondelete='cascade', string="Champ", required=True)
    sign =  fields.Selection([('equal', u'Égal à'), ('inferior', u'Inférieur à'), ('superior', u'Supérieur à'), ('inferior_or_equal', u'Inférieur ou égal à'), ('superior_or_equal', u'Supérieur ou égal à'),
                                ('contain', 'Contient'), ('not_contain', 'Ne contient pas')], string=u'Critère')
    value = fields.Char(string='Valeur')
    boolean_value = fields.Boolean(string=u'Valeur boolean', default=False)
    value_type = fields.Selection(related='field_id.ttype', string='Type de valeur')
    transition_rule_id = fields.Many2one('customisable_workflow.transition_rule', string="Transition", required=True, ondelete='cascade')

    @api.onchange("res_model_id")
    def onchange_res_model(self):
        for record in self:
            if record.res_model_id:
                domain = [('model_id.id', '=', record.res_model_id.id),('ttype', '!=', 'many2many'),
                                                                       ('ttype', '!=', 'one2many'),
                                                                       ('ttype', '!=', 'many2one'),
                                                                       ('ttype', '!=', 'selection'),
                                                                       ('ttype', '!=', 'binary'),
                                                                       ('ttype', '!=', 'date'),
                                                                       ('ttype', '!=', 'datetime'),
                                                                       ('ttype', '!=', 'html'),
                                                                       ('ttype', '!=', 'text')]
                return {'domain': {'field_id': domain}}
    
    @api.constrains('field_id', 'sign', 'value', 'boolean_value')
    def _check_field_id_type(self):
        for record in self:
            ttypes = ['many2many','one2many','many2one','selection','binary','date','datetime','html','text']
            if record.field_id.ttype in ttypes:
                raise exceptions.ValidationError(_('Type de champ non pris en charge!'))
            if record.field_id.ttype == 'char' and (record.sign != 'equal' and record.sign != 'contain' and record.sign != 'not_contain'):
                raise exceptions.ValidationError(_("Critère non compatible.Veuillez choisir le critère 'Égal à' ou 'Contient' ou 'ne contient pas'!"))
            if record.field_id.ttype == 'char' or record.field_id.ttype == 'integer' or record.field_id.ttype == 'float':
                if not record.sign:
                    raise exceptions.ValidationError(_("Veuillez choisir un critère!"))
                if not record.value:
                    raise exceptions.ValidationError(_("Veuillez entrer une valeur!"))
            if (record.field_id.ttype == 'float' or record.field_id.ttype == 'integer') and record.value and not record.value.isdigit():
                raise exceptions.ValidationError(_("Veuillez saisir un nombre!"))    
            
    @api.constrains('field_id', 'res_model_id')
    def _check_field_type_and_res_model(self):
        for record in self:
            if record.field_id and record.res_model_id:
                field_id = self.env['ir.model.fields'].search([('model_id.id', '=', record.res_model_id.id), ('id', '=', record.field_id.id)], limit=1)
                if not field_id:
                    raise exceptions.ValidationError(_('Veuillez choisir un champ qui figure dans le modèle sélectionné!'))
    
    @api.onchange("field_id")
    def onchange_field_id(self):
        for record in self:
            record.boolean_value = False
            if record.field_id.ttype != 'float' and record.field_id.ttype != 'integer' or record.field_id.ttype != 'char':
                record.value = False
                record.sign = False
            if record.field_id.ttype == 'boolean':
                record.boolean_value = True
    
    def check_condition(self, work, conditions_are_checked):
        for condition in self:
            if condition.res_model_id and condition.field_id:
                field_id = condition.field_id
                if field_id.ttype:
                    if condition.sign:
                        if field_id.ttype == 'integer' or field_id.ttype == 'float':
                            if float(condition.value) or float(condition.value) == 0:
                                if work[field_id.name] or work[field_id.name] == 0:
                                    if condition.sign == 'equal':
                                        if work[field_id.name] != float(condition.value):
                                            conditions_are_checked = False
                                        else:
                                            conditions_are_checked = True
                                    if condition.sign == 'inferior':
                                        if not work[field_id.name] < float(condition.value):
                                            conditions_are_checked = False
                                        else:
                                            conditions_are_checked = True
                                    if condition.sign == 'superior':
                                        if not work[field_id.name] > float(condition.value):
                                            conditions_are_checked = False
                                        else:
                                            conditions_are_checked = True
                                    if condition.sign == 'inferior_or_equal':
                                        if not work[field_id.name] <= float(condition.value):
                                            conditions_are_checked = False
                                        else:
                                            conditions_are_checked = True
                                    if condition.sign == 'superior_or_equal':
                                        if not work[field_id.name] >= float(condition.value):
                                            conditions_are_checked = False
                                        else:
                                            conditions_are_checked = True
                        if field_id.ttype == 'char':
                            if condition.sign == 'equal':
                                if work[field_id.name] != condition.value:
                                    conditions_are_checked = False
                                else:
                                    conditions_are_checked = True
                            if condition.sign == 'contain':
                                if condition.value not in work[field_id.name]:
                                    conditions_are_checked = False
                                else:
                                    conditions_are_checked = True
                            if condition.sign == 'not_contain':
                                if condition.value in work[field_id.name]:
                                    conditions_are_checked = False
                                else:
                                    conditions_are_checked = True
                    if field_id.ttype == 'boolean':
                        if work[field_id.name] != condition.boolean_value:
                            conditions_are_checked = False
                        else:
                            conditions_are_checked = True
            return conditions_are_checked