from odoo import fields, models, api

class AssetInventoryLine(models.Model):
    _name = "asset.inventory.line"
    _description = "Ligne Inventaire Immobilisation"

    inventory_id = fields.Many2one(
        "asset.inventory",
        required=True,
        ondelete="cascade"
    )

    asset_id = fields.Many2one(
        "account.asset",
        string="Immobilisation",
        required=True
    )

    asset_code = fields.Char(
        related="asset_id.imo_code",
        string="Code",
        store=True
    )

    category_id = fields.Many2one(
        related="asset_id.asset_group_id",
        string="Catégorie",
        store=True
    )

    model_id = fields.Many2one(
        related="asset_id.model_id",
        string="Catégorie d'immobilisation",
        store=True
    )

    acquisition_date = fields.Date(
        related="asset_id.acquisition_date",
        string="Date mise en service",
        store=True
    )

    state = fields.Selection([
        ("intact", "Intacte"),
        ("damaged", "Endommagé"),
        ("scrap", "Rebut"),
        ("stolen", "Volé"),
        ("transfer", "Transféré"),
    ], default="intact", string="État")
