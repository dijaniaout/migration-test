#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ChecklistResponse(models.Model):
    _name = 'workflow_checklist.checklist_response'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = "Checklist response"

    checklist_id = fields.Many2one('workflow_checklist.checklist', string=u"Checklist", readonly=True, required=True, ondelete="cascade")
    name = fields.Char(string='Nom', related="checklist_id.name")
    model = fields.Char('Related Document Model', index=True)
    res_id = fields.Many2oneReference('Related Decision ID', index=True, model_field='model')
    document_id = fields.Many2one('customisable_workflow.document', string=u"Document", readonly=True, ondelete="cascade")
    step_id = fields.Many2one('customisable_workflow.step', string="Etape", readonly=True, required=True, ondelete="cascade")
    check_response_ids = fields.One2many('workflow_checklist.check_response', 'checklist_response_id', string=u'Checks')
    checker_ids = fields.Many2many('res.users', relation='checkers_of_checklist_response', string=u"Vérificateurs",
        domain=lambda self: [("group_ids", "=", self.env.ref("workflow_checklist.group_user_checker").id)])
    state = fields.Selection([('draft', "Brouillon"),('valid', u'Validé')], default='draft', string='Etat')
    attachment_ids = fields.Many2many('ir.attachment', string="Pièces jointes")
    current_user_can_not_edit_checker = fields.Boolean(u"L'utilisateur ne peut pas modifier la liste des vérificateurs", compute="_compute_can_not_edit_checker")
    total_scores = fields.Float(required=True, string="Note totale", compute="_compute_get_total_scores", store=True, default=0.0)
    decision =  fields.Selection([('accepted', "Accepté"), ('rejected', u"Rejeté"), ('adjourned', "Ajourné")], compute="_compute_get_decision_for_note", string="Décision", store=True)

    def open_one2many_line(self):
        for check_response in self.check_response_ids:
            approval = self.env[check_response.checklist_response_id.model].search([("id", "=", check_response.checklist_response_id.res_id)])
            if check_response.check_id.field_id:
                value = getattr(approval, check_response.check_id.field_id.name)
                if type(value) not in (float, int, str, bool):
                    check_response.field_value =  value.name
                else:
                    check_response.field_value = value
        return {
            'type': 'ir.actions.act_window',
            'name': 'Open Line',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.env.context.get('default_active_id'),
            'target': 'current',
        }

    def action_draft(self):
        self.state = 'draft'

    def action_valid(self):
        self.state = 'valid'

    def _compute_can_not_edit_checker(self):
        for record in self:
            if record.env.user.has_group('workflow_checklist.group_user_checker'):
                record.current_user_can_not_edit_checker = True
            else:
                record.current_user_can_not_edit_checker = False

    @api.depends('check_response_ids.note')
    def _compute_get_total_scores(self):
        for record in self:
            total_scores = sum([check_response.note for check_response in record.check_response_ids])
            record.total_scores = total_scores

    @api.depends('total_scores','state')
    def _compute_get_decision_for_note(self):
        for record in self:
            if record.state == 'valid':
                for note_decision in record.checklist_id.note_decision_ids:
                    if record.total_scores >= note_decision.start_of_interval  and record.total_scores <= note_decision.end_of_interval :
                        record.decision = note_decision.decision