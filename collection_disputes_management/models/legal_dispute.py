from odoo import models, fields,api

class LegalDispute(models.Model):
    _name = 'collection_disputes_management.legal_dispute'
    _description = 'Dossier de Litige'
    _inherit = ['collection.case.base','mail.thread', 'mail.activity.mixin']

    
    _code_unique = models.Constraint(
        'unique(code)',
        "Le code du dossier doit être unique.",
    )

    name = fields.Char(string='Titre', required=True, tracking=True)
    code = fields.Char(string='Code du dossier', required=True)
    workflow_id = fields.Many2one('customisable_workflow.workflow', string='Sous-processus', compute='_compute_workflow_id', store=True)
    base_workflow_id = fields.Many2one('customisable_workflow.workflow', string='Processus', default=lambda self: self._default_base_workflow_id())
    responsable_id = fields.Many2one('res.users', string='Responsable du dossier')
    type_litige_id = fields.Many2one('collection_disputes_management.legal_dispute_type', string='Type', required=True)
    position_banque = fields.Selection([
        ('demandeur', 'Demandeur'),
        ('defendeur', 'Défendeur'),
    ], string='Position de la banque', required=True)
    date_reception = fields.Date(string='Date de création', default=fields.Date.today)
    pays_id = fields.Many2one('res.country', string='Pays')
    description = fields.Text(string='Description')

    collection_dispute_case_id = fields.Many2one('collection.dispute.case',string="Dossier de recouvrement",tracking=True)

    justice_intervention_ids = fields.One2many('collection_disputes_management.justice_intervention', 'legal_dispute_id', string="Interventions de Justice")
    currency_id = fields.Many2one('res.currency', string="Devise", default=lambda self: self.env.company.currency_id)  
    additional_fee_ids = fields.One2many('collection_disputes_management.additional_fee', 'legal_dispute_id', string="Frais annexes")
    total_honorary = fields.Monetary(string="Montant total des honoraires", compute='_compute_fees_totals',store=True, readonly=True)
        
    total_procedure_fee = fields.Monetary(string="Montant total des frais de procédure", compute='_compute_fees_totals',store=True, readonly=True)
    total_additional_fees = fields.Monetary(string="Montant total des frais annexes", compute='_compute_additional_fees', store=True, readonly=True)
    justice_auxiliary_ids = fields.Many2many("collection_disputes_management.justice_auxiliary", "justice_auxiliary_lit", string="Conseiller juridique")
    substitute_id = fields.Many2one('res.users', string="Suppléant")
    judicial_decision_ids = fields.One2many('collection_disputes_management.judicial_decision', 'dispute_case_id', string='Décisions de justice')
    
    def action_open_judicial_decision(self):
        return {
            'name': 'Décisions de justice',
            'type': 'ir.actions.act_window',
            'res_model': 'collection_disputes_management.judicial_decision',
            'view_mode': 'list,form',
            'domain': [('legal_dispute_id', '=', self.id)],
            'context':{'default_legal_dispute_id': self.id}
        }

    def _default_base_workflow_id(self):
        return self.env.ref('collection_disputes_management.workflow_dispute', raise_if_not_found=False)

    @api.depends("base_workflow_id","current_step_id")
    def _compute_workflow_id(self):
        for record in self:
            if record.base_workflow_id and record.base_workflow_id.subprocess_id:
                record.workflow_id = record.base_workflow_id.subprocess_id.id
                if record.current_step_id:
                    record.workflow_id = record.current_step_id.workflow_id.id
            else:
                record.workflow_id = record.base_workflow_id.id

    @api.depends('additional_fee_ids.amount', 'additional_fee_ids.fee_type')
    def _compute_fees_totals(self):
        for record in self:
            honorary_total = 0.0
            procedure_total = 0.0
            if record.additional_fee_ids:
                for fee in record.additional_fee_ids:
                    if fee.fee_type == 'honorary':
                        honorary_total += fee.amount
                    elif fee.fee_type == 'procedure':
                        procedure_total += fee.amount
            record.total_honorary = honorary_total
            record.total_procedure_fee = procedure_total
    
    @api.depends('total_honorary', 'total_procedure_fee')
    def _compute_additional_fees(self):
        for record in self:
            record.total_additional_fees = record.total_honorary  + record.total_procedure_fee 
