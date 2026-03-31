# -*- encoding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class Justification(models.TransientModel):
    _name = 'customisable_workflow.justification_wizard'
    _description = 'Justification'

    justification = fields.Text(string='Justification', required=True)
    decision_id = fields.Many2one('customisable_workflow.step_decision', string='Décision', required=True)
    model = fields.Char('Related Document Model', required=True)
    res_id = fields.Many2oneReference('Related Decision ID', index=True, model_field='model', required=True)
    
    def save(self):
        work = self.env[self.model].search([('id', '=', self.res_id)])
        work._execute_decision(self.decision_id, self.justification)

    