#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Document(models.Model):
    _name = 'customisable_workflow.document'
    _order = "name asc"
    _description = "Document"
    
    name = fields.Char(string='Nom', required=True)
    document_type_id = fields.Many2one("customisable_workflow.document_type", string="Type de document")
    is_required = fields.Boolean(string="Est obligatoire?")
    document = fields.Binary(string='Document')
    document_format_to_generate = fields.Selection([('pdf', 'pdf'), ('docx', 'docx')], string="Format de document à générer", default='pdf')
    allowed_group_ids = fields.Many2many('res.groups', string="Groupes autorisés")
    report_id = fields.Many2one('ir.actions.report', string='Rapport')
    source = fields.Selection([('provided', 'A fournir'), ('generated', 'A générer')], string="Type du document", default='provided', required=True)

    @api.onchange('document_type_id')
    def _onchange_document_type(self):
        for record in self:
            if record.source == 'provided':
                if record.document_type_id:
                    record.name = record.document_type_id.name
    
    @api.constrains('document','report_id')
    def _check_document_and_report(self):
        for record in self:
            if record.source == 'generated':
                if not (record.document or record.report_id):
                    raise ValidationError(_('Veuillez choisir au moins un document ou un rapport.'))
                if record.document and record.report_id:
                    raise ValidationError(_('Vous ne pouvez pas choisir un document et un rapport en même temps.'))
    
    @api.constrains('report_id','document_format_to_generate')
    def _check_document_format_to_generate(self):
        for record in self:
            if record.source == 'generated':
                if record.report_id and record.document_format_to_generate != 'pdf':
                    raise ValidationError(_('Les rapports doivent être générés au format pdf.'))