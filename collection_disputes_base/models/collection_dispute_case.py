#-*- coding:utf-8 -*-
from odoo import models, fields, api,  _
import logging
from datetime import datetime
from datetime import date
from datetime import timedelta
from dateutil.relativedelta import relativedelta
_logger = logging.getLogger(__name__)

class CollectionDisputeCase(models.Model):
    _name = 'collection.dispute.case'
    _inherit = ['collection.case.base', 'mail.thread', 'mail.activity.mixin']
    _order = "create_date desc"
    _description = "Dossier de recouvrement et des litiges"

    _code_unique = models.Constraint(
        'unique(project_code)',
        "Le code du dossier doit être unique.",
    )

    name = fields.Char(string="Intitulé du projet", required=True)
    workflow_id = fields.Many2one('customisable_workflow.workflow', string='Sous-processus', compute='_compute_workflow_id', store=True)
    base_workflow_id = fields.Many2one('customisable_workflow.workflow', string='Processus', default=lambda self: self._default_base_workflow_id())
    customer_id = fields.Many2one('collection_disputes_base.customer', string='Débiteur', required=True)
    customer_activity_sector_id = fields.Many2one('collection_disputes_base.business_sector', string=u"Secteur d'activité du client", related='customer_id.activity_sector_id', store=True)
    customer_legal_status_id = fields.Many2one('collection_disputes_base.legal_status', string="Forme juridique du client", related='customer_id.legal_status_id', store=True)
    customer_city = fields.Char(string="Ville du client", related='customer_id.city', store=True)
    customer_state_id = fields.Many2one('res.country.state', string="Etat du client", related='customer_id.state_id', store=True)
    customer_country_id = fields.Many2one('res.country', string="Pays du client", related='customer_id.country_id', store=True)
    judicial_decision_ids = fields.One2many('collection_disputes_base.judicial_decision', 'dispute_case_id', string='Décisions de justice')

    # Champs page principale
    project_code = fields.Char(string="Code du projet", required=True)
    creation_date = fields.Date(string=u"Date de déclassement", default=fields.Date.context_today)
    case_manager_id = fields.Many2one('res.users', string="Responsable du dossier")
    substitute_id = fields.Many2one('res.users', string="Suppléant")
    tag_ids = fields.Many2many('collection_disputes_base.tag', string="Étiquettes")

    # Onglet Informations – Section "Informations générales"
    country_id = fields.Many2one('res.country', string="Pays", related='customer_id.country_id', required=True)

    # Onglet Informations – Section "Informations financières"
    loan_amount = fields.Monetary(string=u"Montant du prêt")
    unpaid_count = fields.Integer(string=u"Nombre total d'impayés")
    remaining_amount = fields.Monetary(string="Montant créance à recouvrer", compute='_compute_loan_followup_amounts',  readonly=True, store=True)
    # Montant converti en devise société
    provisional_arrears = fields.Monetary(string="Montant de l'arrêté provisoire")
    final_arrears = fields.Monetary(string="Montant de l'arrêté définitif")
    total_recovered = fields.Monetary(string="Montant total recouvré", compute='_compute_total_recovered', store=True)
    total_additional_fees = fields.Monetary(string="Montant total des frais annexes", compute='_compute_additional_fees', store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', string="Devise", default=lambda self: self.env.company.currency_id) 
    legal_dispute_ids = fields.One2many('collection_disputes_base.legal_dispute','collection_dispute_case_id',string="Litiges")
    justice_intervention_ids = fields.One2many('collection_disputes_base.justice_intervention', 'dispute_case_id', string="Interventions de Justice")
    additional_fee_ids = fields.One2many('collection_disputes_base.additional_fee', 'dispute_case_id', string="Frais annexes")
    total_honorary = fields.Monetary(string="Montant total des honoraires", compute='_compute_fees_totals',store=True, readonly=True)
    total_procedure_fee = fields.Monetary(string="Montant total des frais de procédure", compute='_compute_fees_totals',store=True, readonly=True)
    justice_auxiliary_ids = fields.Many2many("collection_disputes_base.justice_auxiliary", "justice_auxiliary_rec", string="Conseiller juridique")
    settlement_ids = fields.One2many('loan.settlement.statement', 'dispute_case_id', string="Arrêtés de situation")
    last_settlement_id = fields.Many2one('loan.settlement.statement', compute='_compute_last_settlement', store=True, string="Dernier arrêté")
    interest_rate = fields.Float(string="Taux d'intérêt (%)")
    late_interest_rate = fields.Float(string="Taux d'intérêt de retard (%)")
    loan_duration = fields.Integer(string="Durée de la créance (mois)")
    transaction_agreement_ids = fields.One2many('collection_disputes_base.transaction_agreement','dispute_case_id',string="Accords Transactionnels")
    # Forward of amortisation lines from the validated aggreement
    amortization_line_ids = fields.One2many('collection_disputes_base.amortization_line','case_id', string="Echéances / Paiements")
    # --- Section suivi du prêt (récapitulatif) ---
    settlement_total_due = fields.Monetary(
        string="Montant à recouvrer (dernier arrêté)",
        currency_field='currency_id',
        compute="_compute_loan_followup_amounts",
        store=True,
        readonly=True,
    )

    amount_to_recover_agreement = fields.Monetary(
        string="Montant à recouvrer (accord validé)",
        currency_field='currency_id',
        compute="_compute_loan_followup_amounts",
        store=True,
        readonly=True,
    )

    amount_unrecoverable = fields.Monetary(
        string="Créance irrécouvrable",
        currency_field='currency_id',
        compute="_compute_loan_followup_amounts",
        store=True,
        readonly=True,
    )
    
    remaining_amount_to_recover = fields.Monetary(string="Montant restant à recouvrer", compute='_compute_remaining_amount_to_recover', store=True, readonly=True)
    signature_date = fields.Date(
        string="Date de signature",
        compute='compute_signature_date', store=True
    )
    off_balance_sheet = fields.Boolean(string="Hors bilan")
    
    @api.depends('transaction_agreement_ids.signature_date')
    def compute_signature_date(self):
        for rec in self:
            agreements = rec.transaction_agreement_ids
            agreement_id = agreements.filtered(lambda a: a.state == 'validated_hd')[:1]
            rec.signature_date = agreement_id.signature_date if agreement_id else False

    @api.depends('remaining_amount', 'total_recovered')
    def _compute_remaining_amount_to_recover(self):
        for rec in self:
            rec.remaining_amount_to_recover = rec.remaining_amount - rec.total_recovered

    @api.depends('transaction_agreement_ids.total_recovered')
    def _compute_total_recovered(self):
        for rec in self:
            agreements = rec.transaction_agreement_ids
            agreement_id = agreements[:1]
            rec.total_recovered = agreement_id.total_recovered if agreement_id else 0.0

    @api.depends(
        'transaction_agreement_ids.state',
        'transaction_agreement_ids.settlement_total_due',
        'transaction_agreement_ids.amount_to_recover_agreement',
        'transaction_agreement_ids.amount_unrecoverable',
        'transaction_agreement_ids.amount_to_recover',
        'last_settlement_id.total_due'
    )
    def _compute_loan_followup_amounts(self):
        for rec in self:
            # Accords du dossier
            agreements = rec.transaction_agreement_ids

            # Accord validé (si présent)
            validated = agreements.filtered(lambda a: a.state == 'validated_hd')[:1]

            # Dernier accord (par ordre de création)
            latest = rec.last_settlement_id

            # Montants
            amount_statement = latest.total_due if latest else 0.0
            amount_agreement = validated.amount_to_recover_agreement if validated else 0.0
            amount_unrecoverable = validated.amount_unrecoverable if validated else 0.0

            # Montant global = avant accord → dernier arrêté / après accord → accord validé
            if validated:
                amount_recover = amount_agreement
            else:
                amount_recover = amount_statement

            rec.settlement_total_due = amount_statement
            rec.amount_to_recover_agreement = amount_agreement
            rec.amount_unrecoverable = amount_unrecoverable
            rec.remaining_amount = amount_recover

    @api.depends( 'remaining_amount', 'last_settlement_id.statement_date', 'last_settlement_id.currency_id', 'currency_id')
    def _compute_remaining_amount_in_company_currency(self):
        for rec in self:
            amt = rec.remaining_amount or 0.0
            company = rec.env.company
            company_currency = company.currency_id

            src_currency = rec.currency_id
            conv_date = rec.last_settlement_id.statement_date or fields.Date.context_today(rec)

            if src_currency == company_currency:
                rec.remaining_amount_in_company_currency = amt
            else:
                rec.remaining_amount_in_company_currency = src_currency._convert(
                    amt, company_currency, company, conv_date
                )
                
    @api.depends('settlement_ids.statement_date')
    def _compute_last_settlement(self):
        for rec in self:
            last = False
            if rec.settlement_ids:
                settlements = rec.settlement_ids.sorted(key=lambda s: s.statement_date or date.min)
                last = settlements[-1] if settlements else False
            rec.last_settlement_id = last

    def _default_base_workflow_id(self):
        return self.env.ref('collection_disputes_base.workflow_recovery', raise_if_not_found=False)

    @api.depends("base_workflow_id", "current_step_id")
    def _compute_workflow_id(self):
        for record in self:
            if record.base_workflow_id and record.base_workflow_id.subprocess_id:
                record.workflow_id = record.base_workflow_id.subprocess_id.id
                if record.current_step_id:
                    record.workflow_id = record.current_step_id.workflow_id.id
            else:
                record.workflow_id = record.base_workflow_id.id
    
    def action_open_amortization_lines(self):
        return {
            'name': 'Échéances / Paiements',
            'type': 'ir.actions.act_window',
            'res_model': 'collection_disputes_base.amortization_line',
            'view_mode': 'list,form',
            'domain': [('case_id', '=', self.id)],
            'context':{'case_id': self.id}
        }
    
    def action_open_legal_dispute(self):
        return {
            'name': 'Litiges',
            'type': 'ir.actions.act_window',
            'res_model': 'collection_disputes_base.legal_dispute',
            'view_mode': 'list,form',
            'domain': [('collection_dispute_case_id', '=', self.id)],
            'context':{'default_collection_dispute_case_id': self.id}
        }
    
    
    
        
    def action_open_judicial_decision(self):
        return {
            'name': 'Décisions de justice',
            'type': 'ir.actions.act_window',
            'res_model': 'collection_disputes_base.judicial_decision',
            'view_mode': 'list,form',
            'domain': [('dispute_case_id', '=', self.id)],
            'context':{'default_dispute_case_id': self.id}
        }
    
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
