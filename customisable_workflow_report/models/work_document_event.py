#-*- coding:utf-8 -*-
from odoo import models, fields, tools, api, _
import logging

_logger = logging.getLogger(__name__)

VIEWABLE_TYPES = ('image', 'video', 'application/pdf', "application/javascript",
            "application/json",
            "text/css",
            "text/html",
            "text/plain")

class WorkDocumentEvent(models.Model):
    _name = 'customisable_workflow_report.work_doc_event'
    _order = "res_id, date desc"
    _auto = False
    _description = "Work document events"

    model = fields.Char('Related Document Model')
    res_id = fields.Many2oneReference('Related Document ID', model_field='model')
    document_model = fields.Char('Reference Document Model')
    reference = fields.Many2oneReference('Reference Document ID',model_field='document_model')
    document_id = fields.Many2one('customisable_workflow.document', string="Document")
    parent_model = fields.Char('Source model')
    parent_id = fields.Many2oneReference('Source document ID', model_field='parent_model')
    step_id = fields.Many2one('customisable_workflow.step', string="Etape", required=True)
    type = fields.Selection([('creation', 'Création'),('validation', 'Validation'),('signature', 'Signature')], "Type d'événement")
    create_date = fields.Date(string='Date de création')
    create_user_id = fields.Many2one('res.users', string="Créateur")
    date = fields.Date(string='Date')
    user_id = fields.Many2one('res.users', string="Utilisateur")
    source_attachment = fields.Many2one('ir.attachment')
    source_mimetype = fields.Char('Source mime type')
    source_previewable = fields.Boolean('Source is previewable', compute="_compute_source_previewable")
    source_attachment_pdf = fields.Many2one('ir.attachment')
    result_attachment = fields.Many2one('ir.attachment')
    result_mimetype = fields.Char('Result mime type')
    result_previewable = fields.Boolean('Result is previewable', compute="_compute_result_previewable")
    result_attachment_pdf = fields.Many2one('ir.attachment')
    current_user_can_act = fields.Boolean(string=u"L'utilisateur peut valider ou signer", compute="_compute_current_user_can_act")
    state = fields.Selection([('validated', u"Validé"),('signed', u"Signé"),('rejected', u"Rejeté")], string=u'État')
    group_name = fields.Char('Nom du groupe', compute="_compute_group_name")
    signature_type = fields.Selection([('manual', "Manuelle"),('electronic', "Electronique")], string='Type de signature')
    version_number = fields.Integer('Numéro de Version', compute='_compute_version_number')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE or REPLACE VIEW %s AS 
                SELECT
                    row_number() OVER() AS id,
                    event.*
                FROM (
                    SELECT
                        wgd.model,
                        wgd.res_id,
                        NULL AS state,
                        wgd.id AS reference,
                        'customisable_workflow.work_generated_document' AS document_model,
                        wgd.document_id as document_id,
                        NULL as parent_model,
                        NULL::INTEGER as parent_id,
                        wgd.step_id,
                        NULL as signature_type,
                        'creation' AS type,
                        NULL::TIMESTAMP AS create_date,
                        NULL::INTEGER AS create_user_id,
                        wgd.create_date AS date,
                        wgd.create_uid AS user_id,
                        NULL::INTEGER AS source_attachment,
                        NULL AS source_mimetype,
                        NULL::INTEGER AS source_attachment_pdf,
                        att.id AS result_attachment,
                        att.mimetype AS result_mimetype,
                        attpdf.id AS result_attachment_pdf,
                        NULL as group_name,
                        NULL as version_number            
                    FROM
                        customisable_workflow_work_generated_document wgd
                    LEFT JOIN ir_attachment att ON att.res_model = 'customisable_workflow.work_generated_document' AND att.res_id = wgd.id
                        AND att.res_field = 'attachment'
                    LEFT JOIN ir_attachment attpdf ON att.res_model = 'customisable_workflow.work_generated_document' AND attpdf.res_id = wgd.id
                        AND attpdf.res_field = 'attachment_pdf'
                    UNION ALL
                    SELECT
                        wgid.model,
                        wgid.res_id,
                        NULL AS state,
                        wgid.id AS reference,
                        'customisable_workflow.work_given_document' AS document_model,
                        wgid.document_id as document_id,
                        NULL as parent_model,
                        NULL::INTEGER as parent_id,
                        wgid.step_id,
                        NULL as signature_type,
                        'creation' AS type,
                        NULL::TIMESTAMP AS create_date,
                        NULL::INTEGER AS create_user_id,
                        att.create_date AS date,
                        att.create_uid AS user_id,
                        NULL::INTEGER AS source_attachment,
                        NULL AS source_mimetype,
                        NULL::INTEGER AS source_attachment_pdf,
                        att.id AS result_attachment,
                        att.mimetype AS result_mimetype,
                        attpdf.id AS result_attachment_pdf,
                        NULL as group_name,
                        NULL as version_number 
                    FROM
                        customisable_workflow_work_given_document wgid
                    LEFT JOIN ir_attachment att ON att.res_model = 'customisable_workflow.work_given_document' AND att.res_id = wgid.id
                        AND att.res_field = 'attachment'
                    LEFT JOIN ir_attachment attpdf ON att.res_model = 'customisable_workflow.work_given_document' AND attpdf.res_id = wgid.id
                        AND attpdf.res_field = 'attachment_pdf'
                    UNION ALL
                    SELECT
                        wdv.model,
                        wdv.res_id,
                        wdv.state as state,
                        wdv.id as reference,
                        'customisable_workflow_validation.work_doc_to_validate' as document_model,
                        sv.document_id,
                        wdv.parent_model as parent_model,
                        wdv.parent_id as parent_id,
                        wdv.step_id,
                        NULL as signature_type,
                        'validation' as type,
                        wdv.create_date as create_date,
                        wdv.create_uid as create_user_id,
                        wdv.action_date as date,
                        wdv.actor_user_id as user_id,
                        att.id AS source_attachment,
                        att.mimetype AS source_mimetype,
                        attpdf.id AS source_attachment_pdf,
                        att.id AS result_attachment,
                        att.mimetype AS result_mimetype,
                        attpdf.id AS result_attachment_pdf,
                        NULL as group_name,
                        NULL as version_number 
                    FROM
                        customisable_workflow_validation_work_doc_to_validate wdv
                    INNER JOIN customisable_workflow_validation_step_validation sv
                        ON sv.id = wdv.origin_id
                    LEFT JOIN ir_attachment att ON att.res_model = 'customisable_workflow_validation.work_doc_to_validate' and att.res_id = wdv.id
                        AND att.res_field = 'source_document'
                    LEFT JOIN ir_attachment attpdf ON attpdf.res_model = 'customisable_workflow_validation.work_doc_to_validate' and attpdf.res_id = wdv.id
                        AND attpdf.res_field = 'source_document_pdf'
                    UNION ALL
                    SELECT
                        wsd.model,
                        wsd.res_id,
                        wsd.state as state,
                        wsd.id as reference,
                        'customisable_workflow_signature.work_signed_document' as document_model,
                        ss.document_id as document_id,
                        wsd.parent_model as parent_model,
                        wsd.parent_id as parent_id,
                        wsd.step_id,
                        wsd.signature_type as signature_type,
                        'signature' as type,
                        wsd.create_date as create_date,
                        wsd.create_uid as create_user_id,
                        wsd.action_date as date,
                        wsd.actor_user_id as user_id,
                        att.id AS source_attachment,
                        att.mimetype AS source_mimetype,
                        attpdf.id AS source_attachment_pdf,
                        attres.id AS result_attachment,
                        attrespdf.mimetype AS result_mimetype,
                        attrespdf.id AS result_attachment_pdf,
                        NULL as group_name,
                        NULL as version_number 
                    FROM
                        customisable_workflow_signature_work_signed_document wsd
                    INNER JOIN customisable_workflow_signature_step_signature ss
                        ON ss.id = wsd.origin_id
                    LEFT JOIN ir_attachment att ON att.res_model = 'customisable_workflow_signature.work_signed_document' and att.res_id = wsd.id
                        AND att.res_field = 'source_document'
                    LEFT JOIN ir_attachment attpdf ON attpdf.res_model = 'customisable_workflow_signature.work_signed_document' and attpdf.res_id = wsd.id
                        AND attpdf.res_field = 'source_document_pdf'
                    LEFT JOIN ir_attachment attres ON attres.res_model = 'customisable_workflow_signature.work_signed_document' and attres.res_id = wsd.id
                        AND attres.res_field = 'result_document'
                    LEFT JOIN ir_attachment attrespdf ON attrespdf.res_model = 'customisable_workflow_signature.work_signed_document' and attrespdf.res_id = wsd.id
                        AND attrespdf.res_field = 'result_document_pdf'
                ) event
                """ % ( self._table))
    
    def _compute_current_user_can_act(self):
        for record in self:
            if record.type == 'validation':
                doc = self.env[record.document_model].search([('id', '=', record.reference)])
                record.current_user_can_act = doc.current_user_can_act
            elif record.type == 'signature':
                doc = self.env[record.document_model].search([('id', '=', record.reference)])
                record.current_user_can_act = doc.current_user_can_act
            elif record.type == 'creation':
                doc = self.env[record.model].search([('id', '=', record.res_id)])
                record.current_user_can_act = doc.current_user_can_act
            else:
                record.current_user_can_act = False
    
    @api.depends('source_mimetype', 'source_attachment_pdf')
    def _compute_source_previewable(self):
        for event in self:
            source_previewable = False
            if event.source_mimetype:
                for viewable_type in VIEWABLE_TYPES:
                    if viewable_type in event.source_mimetype:
                        source_previewable = True
                        break
            event.source_previewable = source_previewable or event.source_attachment_pdf
    
    @api.depends('result_mimetype', 'result_attachment_pdf')
    def _compute_result_previewable(self):
        for event in self:
            result_previewable = False
            if event.result_mimetype:
                for viewable_type in VIEWABLE_TYPES:
                    if viewable_type in event.result_mimetype:
                        result_previewable = True
            event.result_previewable = result_previewable or event.result_attachment_pdf
    
    @api.depends('document_id')
    def _compute_group_name(self):
        for event in self:
            if event.document_id.name:
                event.group_name = event.document_id.name
            else:
                event.group_name = ''

    @api.depends('res_id', 'document_id')
    def _compute_version_number(self):
        for event in self:
            if event.res_id and event.document_id:   
                same_versions = self.search([
                    ('res_id', '=', event.res_id),
                    ('document_id', '=', event.document_id.id),
                    ('date', '<=', event.date),
                ])
                if not same_versions:
                    event.version_number = 1 
                else:
                    event.version_number = len(same_versions)
            else:
                event.version_number = 1