#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.fields import Domain
from datetime import datetime


class TransitionHistory(models.Model):
    _name = 'customisable_workflow.transition_history'
    _description = 'step history'

    model = fields.Char('Related Document Model', index=True, required=True)
    res_id = fields.Many2oneReference('Related Decision ID', index=True, model_field='model', required=True)
    step_from_id = fields.Many2one('customisable_workflow.step', string="Etape précédente", ondelete='cascade')
    step_to_id = fields.Many2one('customisable_workflow.step', string="Etape suivante", ondelete='cascade')
    date = fields.Datetime(string="Date", default=fields.Datetime.now, required=True)
    user_id = fields.Many2one('res.users', string="Utilisateur", required=True)
    justification = fields.Text(string='Justification')
    workflow_id = fields.Many2one('customisable_workflow.workflow', string='Processus', related='step_to_id.workflow_id')
    
    # Override to hide pending history entries (step_to field empty) if not requested from the context
    @api.model
    def _search(self, domain, *args, **kwargs):
        if not 'show_all' in self.env.context:
            domain = Domain.AND([Domain('step_to_id', '!=', False), domain])
        return super()._search(domain, *args, **kwargs)