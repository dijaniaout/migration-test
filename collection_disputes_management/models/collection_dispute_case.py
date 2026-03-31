#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class CollectionDisputeCase(models.Model):
    _inherit = 'collection.dispute.case'

    guarantor_ids = fields.Many2many('collection_disputes_management.guarantor', 'guarantor_rec', string='Garants')
    collateral_ids = fields.One2many('collection_disputes_management.collateral', 'dispute_case_id', string="Garanties")
    guarantees_realisation_date = fields.Date(string=u"Date de réalisation des garanties")
    
    payment_incident_ids = fields.One2many('payment.incident', 'dispute_case_id', string="Incidents de paiement")
    
    def action_open_payment_incident(self):
        return {
            'name': 'Incidents de paiement',
            'type': 'ir.actions.act_window',
            'res_model': 'payment.incident',
            'view_mode': 'list,form',
            'domain': [('dispute_case_id', '=', self.id)],
            'context':{'default_dispute_case_id': self.id}
        }
