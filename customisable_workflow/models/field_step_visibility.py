#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class FieldStepVisibility(models.Model):
    _name = 'customisable_workflow.field_step_visibility'
    _description = 'Fields visibility or readonly or required by step'

    field_id = fields.Many2one('ir.model.fields',
                                ondelete='cascade', string="Champ", required=True)
    required_step_id = fields.Many2one("customisable_workflow.step", string="Obligatoire à l'étape", ondelete="cascade")
    readonly_step_id = fields.Many2one("customisable_workflow.step", string="Lecture seule à l'étape", ondelete="cascade")
    visible_step_id = fields.Many2one("customisable_workflow.step", string="Visible à l'étape ", ondelete="cascade")
    workflow_id = fields.Many2one("customisable_workflow.workflow", string="Processus", ondelete="cascade")
    res_model_id = fields.Many2one(related="workflow_id.res_model_id", store=True)

    _field_uniq = models.Constraint('unique(field_id, workflow_id)', 'Les valeurs des champs étape, processus et champ doivent être uniques.')

    @api.onchange("workflow_id")
    def onchange_res_model(self):
        for record in self:
            if record.workflow_id:
                domain = [('model_id.model', '=', record.workflow_id.res_model_id.model),('readonly', '=', False),('ttype', '!=', 'many2many'),('ttype', '!=', 'one2many')]
                return {'domain': {'field_id': domain}}

    @api.constrains('required_step_id','readonly_step_id')
    def _not_same_step(self):
        for record in self:
            if record.required_step_id and record.readonly_step_id:
                if record.required_step_id == record.readonly_step_id:
                    raise ValidationError(_("Un champs à lecture seul ne peut etre obligatoire sur la meme étape"))