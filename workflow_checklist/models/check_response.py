from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CheckResponse(models.Model):
    _name = 'workflow_checklist.check_response'
    _description = "Check response"

    check_id  = fields.Many2one('workflow_checklist.check', string='Check', required=True, ondelete="cascade")
    name = fields.Char(string='Nom', related="check_id.name")
    maximum_score = fields.Float(string='Note maximale', related="check_id.maximum_number_of_points")
    note = fields.Float(string='Note', required=True, default=0.0)
    comment = fields.Text(string='Commentaire')
    checklist_response_id = fields.Many2one('workflow_checklist.checklist_response', string=u"Checklist", required=True, ondelete="cascade")
    type_response = fields.Selection(related="check_id.type_response", string="Type de réponse", readonly=False)
    yes_or_no = fields.Selection([('yes', 'Oui'), ('no', 'Non')], string=u'Oui/Non', default='no')
    choice_id  = fields.Many2one('workflow_checklist.ckeck.multiple_choice', string='choix Possible', domain="[('check_id', '=', check_id)]")
    field_value = fields.Char(string="Information du dossier")

    _unique_response_constraint = models.Constraint('unique(check_id,checklist_response_id)', "Une question ne peut avoir qu'une réponse dans une checklist.")

    @api.onchange('note')
    def _onchange_check_note(self):
        for record in self:
            if record.note > record.maximum_score:
                return {
                            'warning': {'title': "Warning",
                            'message': "Vous ne pouvez pas donner une note supérieure à la note maximale."}
                        }

    @api.constrains('maximum_score','note')
    def _check_note(self):
        for record in self:
            if record.note > record.maximum_score:
                raise ValidationError(_("Vous ne pouvez dépasser la note maximale attribuée à une réponse."))

    @api.constrains
    def _get_choices(self):
        for record in self:
            choices = self.env['ckeck.multiple_choice'].search([('section_id', '=', record.check_id.section_id.id)])
            for choice in choices:
                record.choice_id = choice.id
