# Copyright 2026 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    supplier_calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Default Supplier Calendar",
        help="Calendar used by the vendors with Default Supplier Calendar as Delay "
        "Calendar Type.",
    )
