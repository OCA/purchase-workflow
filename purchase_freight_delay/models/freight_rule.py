# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class FreightRule(models.Model):
    _name = "freight.rule"
    _description = "Freight container"
    _rec_name = "display_name"
    _order = "freight_type, partner_src_id, partner_dest_id"

    display_name = fields.Char(compute="_compute_display_name", store=True)
    sequence = fields.Integer(copy=False)
    partner_src_id = fields.Many2one(
        comodel_name="res.partner",
        string="Boarding",
        help="Boarding place where goods comes from."
        "\nFill reference field on partner for a better display",
    )
    partner_dest_id = fields.Many2one(
        comodel_name="res.partner",
        domain=lambda self: self._get_partner_dest_domain(),
        string="Landing",
        help="Landing place where goods are delivered. Addresses of your warehouses",
    )
    logistics_partner_id = fields.Many2one(comodel_name="res.partner")
    freight_type = fields.Selection(
        required=True,
        default="ship",
        selection=[
            ("ship", "Ship"),
            ("truck", "Truck"),
            ("train", "Train"),
            ("plane", "Plane"),
        ],
    )
    duration = fields.Integer(help="Duration in days")

    cols = {
        "names": "partner_src_id, partner_dest_id, logistics_partner_id, freight_type, duration"
    }
    _sql_constraints = [
        (
            "src_dest_partner_type_duration_unique",
            "UNIQUE(%(names)s)" % cols,
            "Fields combination '%(names)s' must be unique" % cols,
        )
    ]

    def _get_partner_dest_domain(self):
        partners = self.env["stock.warehouse"].search([]).mapped("partner_id")
        return [("id", "in", partners.ids)]

    @api.depends(
        "partner_src_id",
        "partner_src_id.ref",
        "partner_dest_id",
        "partner_dest_id.ref",
        "duration",
        "freight_type",
    )
    def _compute_display_name(self):
        FREIGHT = {key: val for key, val in self._fields["freight_type"].selection}
        for rec in self:
            name = FREIGHT.get(rec.freight_type)
            if rec.duration:
                name = _(f"{name} {rec.duration} days")
            if rec.partner_src_id:
                partner = rec.partner_src_id.ref or rec.partner_src_id.name
                name = f"{name}, {partner}"
            if rec.partner_dest_id:
                partner = rec.partner_dest_id.ref or rec.partner_dest_id.name
                name = f"{name} ➡️ {partner}"
            rec.display_name = name
