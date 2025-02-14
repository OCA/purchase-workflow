# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purchase_requisition = fields.Selection(
        selection=[
            ("rfq", "Create a draft purchase order"),
            ("tenders", "Propose a call for tenders"),
        ],
        string="Procurement",
        default="rfq",
        help="Create a draft purchase order: Based on your product configuration,"
        "the system will create a draft purchase order. \nPropose a call for tender : "
        "If the 'purchase_requisition' module is installed and this option is "
        "selected, the system will create a draft call for tender.",
    )
