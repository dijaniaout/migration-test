#-*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ChecklistNoteDecision(models.Model):
    _name = 'workflow_checklist.checklist_note_decision'
    _description = "decision on Checklist"

    start_of_interval = fields.Float(string=u"Début d'intervalle", required=True)
    end_of_interval = fields.Float(string="Fin d'intervalle", required=True)
    decision =  fields.Selection([('accepted', "Accepté"), ('rejected', u"Rejeté"), ('adjourned', "Ajourné")], string="Décision", required = True)
    checklist_id = fields.Many2one('workflow_checklist.checklist', string=u"check list", required=True, ondelete="cascade")

    def _search_the_overlapping_interval(self, start_of_interval, end_of_interval):
        return self.env['workflow_checklist.checklist_note_decision'].search(['|','&',('start_of_interval','>=',start_of_interval), ('start_of_interval','<=',end_of_interval), '&', ('end_of_interval','>=',start_of_interval), ('end_of_interval','<=',end_of_interval)])

    @api.constrains('checklist_id','start_of_interval', 'end_of_interval')
    def _check_time_overlap(self):
        for record in self:
            if record.start_of_interval and record.end_of_interval:
                if record.end_of_interval <= record.start_of_interval:
                    raise ValidationError(_("La fin d'intervalle doit être supérieure au début de l'intervalle"))
                coincident_intervals= record._search_the_overlapping_interval(record.start_of_interval,record.end_of_interval)
                if coincident_intervals:
                    for interval in coincident_intervals:
                        if record.checklist_id == interval.checklist_id:
                            if interval.id != record.id:
                                raise ValidationError(_("Il y'a des intervalles qui se chevauchent pour la checklist: %s")% self.checklist_id.name)
