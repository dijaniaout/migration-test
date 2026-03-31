#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StepDecision(models.Model):
    _name = 'customisable_workflow.step_decision'
    _description = 'Decision to make'
    _order = 'sequence asc'

    name = fields.Char('Nom', required=True)
    sequence = fields.Integer(default=10, help="Donne l'ordre de séquence lors de l'affichage d'une liste d'enregistrements.")
    highlight_button = fields.Boolean('Mettre en avant ?')
    step_id = fields.Many2one('customisable_workflow.step', string="Etape", required=True, ondelete='cascade')
    workflow_id = fields.Many2one('customisable_workflow.workflow', string="Processus", related="step_id.workflow_id", store=True)
    need_a_justification = fields.Boolean("A besoin d'une justification?")
    transition_rule_id = fields.Many2one('customisable_workflow.transition_rule', string="Transition automatique")
    expected_document_state_ids = fields.One2many('customisable_workflow.expected_document_state', 'step_decision_id', string=u"États attendus des documents")
    is_manual_decision = fields.Boolean(u"Décision manuelle?", default=True)
    python_compute = fields.Text(string='Python Code', help="Écrivez le code Python que l'action exécutera. Certaines variables "
                            "sont disponibles pour l'utilisation ; l'aide sur les expressions Python est donnée dans l'onglet d'aide.")
    button_visibility_criterion = fields.Char(u"Critère d'invisibilité du bouton", help="Ce champ contient des critères pour la visibilité du bouton. "
                                                   "Exemple : 'amount_total > 1000 ou state != 'draft' ou parent_id != False")
        
    transition_options = fields.Selection(
            selection=[
                ('current_process_step', 'Etape du processus actuel'),
                ('subprocess', 'Sous-processus')
            ],
            string="Options de transitions",
            required=True,
            default='current_process_step'
        )
    step_id = fields.Many2one('customisable_workflow.step', string="Etape", required=True, ondelete='cascade')
    subprocess_id = fields.Many2one(
        'customisable_workflow.workflow',
        string='Sous-processus',
        domain="[('type', '=', 'process'), ('id', '!=', workflow_id)]"
    )
    target_step_id = fields.Many2one(
        'customisable_workflow.step', 
        string="Etape où le dossier est renvoyé", 
        ondelete="cascade",
        domain="""
            [
                ('workflow_id', '=', 
                    (transition_options == 'current_process_step' and workflow_id) or 
                    (transition_options == 'subprocess' and subprocess_id)
                ),
                ('id', '!=', step_id)
            ]
        """
    )

    @api.constrains('subprocess_id')
    def _set_first_sub_process_step_id(self):
        for record in self:
            if record.subprocess_id and record.subprocess_id.start_step_id:
                record.target_step_id = record.subprocess_id.start_step_id.id
                
    @api.constrains('step_id','target_step_id')
    def _check_current_step(self):
        for record in self:
            if record.target_step_id.id == record.step_id.id:
                raise ValidationError(_("Attention! Une décision ne peut pas rester sur la même étape."))
    
    @api.onchange('transition_rule_id')
    def _onchange_transition(self):
        for record in self:
            if not record.transition_rule_id:
                record.is_manual_decision = True
    
    @api.onchange('subprocess_id')
    def _onchange_subprocess_id(self):
        for record in self:
            if record.subprocess_id:
                record.target_step_id = record.subprocess_id.start_step_id.id
    
    @api.onchange('transition_options')
    def _onchange_transition_options(self):
        for record in self:
            if record.transition_options:
                record.target_step_id = False
                record.subprocess_id = False