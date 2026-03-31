from odoo import models, fields, api, Command

class AssetInventory(models.Model):
    _name = "asset.inventory"
    _description = "Asset Inventory"
    _inherit = ['customisable_workflow.work', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Code",
        readonly=True,
        copy=False,
        default="New"
    )

    start_date = fields.Date(string="Date de début", required=True)
    end_date = fields.Date(string="Date de fin")

    employee_id = fields.Many2one(
        "hr.employee",
        string="Responsable",
        required=True
    )

    site_id = fields.Many2one(
        "asset.site",
        string="Site",
        required=True
    )

    state = fields.Selection([
        ("planned", "Planifié"),
        ("in_progress", "En cours"),
        ("validation", "En validation"),
        ("done", "Terminé")
    ], default="planned", tracking=True)

    line_ids = fields.One2many(
        "asset.inventory.line",
        "inventory_id",
        string="Immobilisations"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("asset.inventory")
        return super().create(vals_list)
        
    @api.onchange('site_id')
    def _onchange_site_id(self):
        if not self.site_id:
            self.line_ids = [Command.clear()]
            return

        assets = self.site_id.asset_ids

        self.line_ids = [
            Command.clear()
        ] + [
            Command.create({
                'asset_id': asset.id
            }) for asset in assets
        ]