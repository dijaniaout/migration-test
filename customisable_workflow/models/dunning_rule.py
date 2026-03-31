#-*- coding:utf-8 -*-
from odoo import models, fields, tools, api

class DunningRule(models.Model):
    _name = 'customisable_workflow.dunning.rule'
    _description = "Règle de relance"

    name = fields.Char(u'Libellé')
    field_id = fields.Many2one('ir.model.fields', domain="[('model_id.model', '=', 'customisable_workflow.work'), '|', ('ttype', '=', 'float'), ('ttype', '=', 'integer')]", string=u"Champ", required=True, ondelete='cascade')
    sign = fields.Selection([('less_than', u'Inférieur à'),
                                 ('less_than_or_equal_to', u'Inférieur ou égal à'),
                                 ('more_than', u'Supérieur à'),
                                 ('more_than_or_equal_to', u'Supérieur ou égal à'),
                                 ('is_equal_to', u'Est égal à'),
                                 ('is_defined', 'Est défini'),
                                 ('is_not_defined', 'N\'est pas défini')], string=u"Critère", default="less_than", required=True)
    number = fields.Float(string="Valeur numérique")
    boolean_value = fields.Boolean(string="Valeur booléenne")
    value_type = fields.Selection(related='field_id.ttype', string='Type de la valeur')

    def name_get(self):
        result = []
        sign_mapping = {
            'less_than': ' inférieur à ',
            'less_than_or_equal_to': ' inférieur ou égal à ',
            'more_than': ' supérieur à ',
            'more_than_or_equal_to': ' supérieur ou égal à ',
            'is_equal_to': ' est égal à ',
            'is_defined': ' est défini ',
            # Ajoutez de nouvelles valeurs au besoin
        }

        for record in self:
            sign = sign_mapping.get(record.sign, " n'est pas défini ")
            name = record.field_id.field_description + sign + str(record.number)
            result.append((record.id, name))
        return result
