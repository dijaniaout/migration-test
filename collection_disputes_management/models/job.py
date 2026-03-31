from odoo import api, fields, models

class Job(models.Model):
    _name = "collection_disputes_management.job"
    _description = "Métier"
    name = fields.Char(string=u"Métier", required=True)