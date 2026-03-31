#-*- coding:utf-8 -*-
from odoo import models, fields, api,  _
import logging

_logger = logging.getLogger(__name__)

class Customer(models.Model):
    _name = 'collection_disputes_management.customer'
    _inherits = {'res.partner': 'partner_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Client"
    activity_sector_id = fields.Many2one("collection_disputes_management.business_sector", string="Secteur d'activité")
    legal_status_id = fields.Many2one("collection_disputes_management.legal_status", string="Forme juridique")
    partner_id = fields.Many2one(
        'res.partner',
        required=True,
        ondelete='cascade',
        delegate=True
    )


    @api.onchange('company_type')
    def onchange_company_type(self):
        self.is_company = (self.company_type == 'company')
        
    def create_company(self):
        self.ensure_one()
        return self.partner_id.create_company()