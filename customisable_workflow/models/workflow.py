#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)
class Workflow(models.Model):
    _name = 'customisable_workflow.workflow'
    _order = "name asc"
    _description = "Workflow"

    name = fields.Char(string='Nom', required=True)
    step_ids = fields.One2many('customisable_workflow.step', 'workflow_id', string='Etapes du processus', copy=True)
    start_step_id = fields.Many2one('customisable_workflow.step', string=u'Etape de début', domain="[('workflow_id', '=', id)]")
    has_documents_to_give = fields.Boolean(string="Has documents to give", compute="_compute_has_documents_to_give")
    has_documents_to_generate = fields.Boolean(string="Has documents to generate", compute="_compute_has_documents_to_generate")
    has_documents_to_sign = fields.Boolean(string="A un document à signer", compute="_compute_has_documents_to_sign")
    maximum_processing_time = fields.Integer(string="Temps de traitement maximum")
    processing_start_step_id = fields.Many2one('customisable_workflow.step', string=u"Etape de début de traitement")
    processing_end_step_id = fields.Many2one('customisable_workflow.step', string="Etape de fin de traitement")
    processing_expiraton_step_id = fields.Many2one('customisable_workflow.step', string=u"Etape en retard")
    processing_time_feature_enabed = fields.Boolean('Etape obligatoire', compute='_compute_processing_time_feature_enabed', default=False)
    res_model_id = fields.Many2one('ir.model', string=u'Modéle', ondelete='cascade')
    field_step_visibility_ids = fields.One2many("customisable_workflow.field_step_visibility", 'workflow_id', string=u"Visibilités champs par étape")
    type = fields.Selection(
         selection=[
             ('process', 'Etape'),
             ('subprocess', 'Sous-processus')
         ],
         string="Débuter par",
         required=True,
         default='process', ondelete={'process': 'set default', 'subprocess':'set default'}
     )
    subprocess_id = fields.Many2one('customisable_workflow.workflow', string='Sous-processus de début', domain="[('type', '=', 'process'), ('id', '!=', id)]")
    dunning_ids = fields.One2many("customisable_workflow.dunning", "workflow_id", string="Relances")

    @api.depends('maximum_processing_time')
    def _compute_processing_time_feature_enabed(self):
        for workflow in self:
            if workflow.maximum_processing_time > 0:
                workflow.processing_time_feature_enabed = True
            else:
                workflow.processing_time_feature_enabed = False

    def _compute_has_documents_to_give(self):
        for workflow in self:
            workflow.has_documents_to_give = any(step.provided_document_ids for step in workflow.step_ids)
    
    def _compute_has_documents_to_generate(self):
        for workflow in self:
            workflow.has_documents_to_generate = any(step.generated_document_ids for step in workflow.step_ids)
    
    def _compute_has_documents_to_sign(self):
        for workflow in self:
            workflow.has_documents_to_sign = any(step.document_to_sign_ids for step in workflow.step_ids)