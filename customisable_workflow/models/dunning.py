#-*- coding:utf-8 -*-
from odoo import models, fields, tools, api

class Dunning(models.Model):
    _name = 'customisable_workflow.dunning'
    _description = "Relances"

    name = fields.Char(string="Nom", required=True)
    dunning_rule_ids = fields.Many2many("customisable_workflow.dunning.rule", "customisable_workflow_dunning_rule_dunning_rel", string=u"Règles de relance")
    notification_ids = fields.Many2many("banking_customisable_workflow.notification_type", "banking_customisable_workflow_notification_type_dunning_rel", string="Notifications")
    workflow_id = fields.Many2one("customisable_workflow.workflow", string="Processus", ondelete="cascade", required=True)
    cumulative = fields.Boolean(string="Cumulative", default=False)