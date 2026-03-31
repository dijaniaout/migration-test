
#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Step(models.Model):
    _name = 'customisable_workflow.step'
    _order = "workflow_id, id"
    _description = "Workflow step"

    name = fields.Char(string='Nom', required=True)
    description = fields.Text(string="Description")
    workflow_id = fields.Many2one('customisable_workflow.workflow', string="Processus", required=True, ondelete='cascade')
    provided_document_ids = fields.Many2many('customisable_workflow.document', 'customisable_workflow_document_step_provided_document_rel', string=u"Documents à fournir", domain="[('source','=','provided')]")
    generated_document_ids = fields.Many2many('customisable_workflow.document', 'customisable_workflow_document_step_generated_document_rel', string=u"Documents à produire", domain="[('source','=','generated')]")
    notification_type_ids = fields.Many2many('banking_customisable_workflow.notification_type', 'banking_customisable_workflow_step_ntification_rel',  string="Notifications à envoyer")
    allowed_user_ids = fields.Many2many('res.users', string='Individus autorisés')
    allowed_group_ids = fields.Many2many('res.groups', string="Groupes autorisés")
    all_allowed_user_ids = fields.Many2many('res.users', compute="_compute_all_users")
    is_automatic_step = fields.Boolean(string=u"Est automatique", default=False)
    step_decision_ids = fields.One2many('customisable_workflow.step_decision', 'step_id', string=u'Décisions possibles')
    criticity = fields.Selection([('info', 'Normale'),
                                    ('success', 'Ok'),
                                    ('warning', 'Avertissement'),
                                    ('danger', 'Critique')
                                ], string=u"Criticité de l'étape", default='info',
                                    help="La criticité est matérialisée par des couleurs,\n"
                                    "Normale: L'étape est dans le chemin normal du processus. Une indication en bleu sera appliquée.\n"
                                    "OK: Pour une étape qui correspond à un aboutissement du processus. Une indication en vert sera appliquée .\n"
                                    "Avertissement: Pour attirer l'attention de l'agent et l'emmener à prendre une action. Une indication en jaune sera appliquée.\n"
                                    "Critique: Pour une étape considérée comme un échec du processus. Une indication en rouge sera appliquée.")
    visible_to_group_ids = fields.Many2many('res.groups', 'step_visibility', string=u"Groupes auxquels l'étape est visible")
    readonly_group_ids = fields.Many2many('res.groups', 'step_readonly', string=u"Groupes pour lesquels l'étape est en lecture seule")
    corresponding_state = fields.Char(string="Statut homologue", help="Permet de dire qu'une étape du processus (dynamique) correspond à tel statut "
                                      "du processus statique d'un objet Odoo. Dans ce cas, tout changement détecté vers ce statut aura "
                                      "comme conséquence de déplacer le processus à l'étape correspondante. Ainsi ce champ sera utile dans le "
                                      "remplacement d'un processus statique par un processus dynamique tout en gardant un mapping entre "
                                      "statuts et étapes.")

    @api.depends('allowed_user_ids','allowed_group_ids')
    def _compute_all_users(self):
        for record in self:
            users = record.env['res.users']
            if record.allowed_user_ids:
                users |= record.allowed_user_ids
            if record.allowed_group_ids:
                for group in record.allowed_group_ids:
                    users |= group.user_ids
            record.all_allowed_user_ids = users
    
    @api.constrains('is_automatic_step','step_decision_ids')
    def _set_first_step_if_not_set(self):
        for step in self:
            if step.is_automatic_step and len(step.step_decision_ids) > 1:
                raise ValidationError(_("Une étape automatique ne peut pas avoir plus d'une décision possible."))
    
    @api.constrains('allowed_group_ids','visible_to_group_ids')
    def _check_visible_step(self):
        for step in self:
            if step.allowed_group_ids and step.visible_to_group_ids:
                for allowed_group in step.allowed_group_ids:
                    authorized_groups_are_visible = False
                    for step_visible_group in step.visible_to_group_ids:
                        if allowed_group.id == step_visible_group.id:
                            authorized_groups_are_visible = True
                            break
                    if authorized_groups_are_visible == False:
                        raise ValidationError(_("Les groupes autorisés doivent avoir une visibilité sur l'étape."))
                        break
    
    @api.constrains('step_decision_ids')
    def _check_unique_target_step_id(self):
        for step in self:
            target_step_ids = step.step_decision_ids.mapped('target_step_id')
            for target_step_id in target_step_ids:
                decisions_count = step.step_decision_ids.filtered(lambda decision: decision.target_step_id == target_step_id)
                if len(decisions_count) > 1:
                    raise ValidationError(_("Attention ! Deux décisions différentes ne peuvent pas aller sur la même étape."))