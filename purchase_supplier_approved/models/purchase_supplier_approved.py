# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseSupplierApproved(models.Model):
    _name = "purchase.supplier.approved"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Approved Supplier for Product"
    _order = "product_tmpl_id, partner_id, date_from desc"
    _rec_name = "name"

    partner_id = fields.Many2one(
        "res.partner",
        string="Supplier",
        required=True,
        tracking=True,
        domain="[('is_company', '=', True), ('supplier_rank', '>', 0)]",
        help="Approved supplier for the product",
    )
    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Product Template",
        required=True,
        tracking=True,
        help="Product template for which the supplier is approved",
    )
    date_from = fields.Date(
        string="Valid From",
        required=True,
        tracking=True,
        default=fields.Date.context_today,
        help="Date from which the supplier approval is valid",
    )
    date_to = fields.Date(
        string="Valid To",
        tracking=True,
        help="Date until which the supplier approval is valid. "
        "Leave empty for no expiration",
    )
    active = fields.Boolean(
        default=True,
        tracking=True,
        help="Uncheck to deactivate the supplier approval",
    )
    name = fields.Char(
        compute="_compute_name",
        store=True,
    )

    @api.depends("partner_id", "product_tmpl_id")
    def _compute_name(self):
        for record in self:
            if record.partner_id and record.product_tmpl_id:
                record.name = (
                    f"{record.partner_id.name} - {record.product_tmpl_id.name}"
                )
            else:
                record.name = _("New Approved Supplier")

    @api.constrains("date_from", "date_to")
    def _check_date_validity(self):
        for record in self:
            if record.date_to and record.date_from > record.date_to:
                raise ValidationError(
                    _("Valid From date must be before Valid To date.")
                )

    @api.constrains("partner_id", "product_tmpl_id", "date_from", "date_to", "active")
    def _check_unique_approval(self):
        for record in self:
            if not record.active:
                continue

            domain = [
                ("partner_id", "=", record.partner_id.id),
                ("product_tmpl_id", "=", record.product_tmpl_id.id),
                ("active", "=", True),
                ("id", "!=", record.id),
            ]

            # Check for overlapping date ranges
            # Two date ranges [start1, end1] and [start2, end2] overlap if:
            # start1 <= end2 and start2 <= end1 (where None means no end date)
            if record.date_to:
                # New record has an end date
                domain.extend(
                    [
                        "|",
                        # has no end date and starts before new record ends
                        "&",
                        ("date_to", "=", False),
                        ("date_from", "<=", record.date_to),
                        # has end date and ranges overlap
                        "&",
                        ("date_to", "!=", False),
                        ("date_from", "<=", record.date_to),
                        "|",
                        ("date_to", ">=", record.date_from),
                        ("date_to", "=", False),
                    ]
                )
            else:
                # New record has no end date
                domain.extend(
                    [
                        "|",
                        # no end date and starts on or after new record
                        "&",
                        ("date_to", "=", False),
                        ("date_from", ">=", record.date_from),
                        # has end date and starts before new record's start
                        "&",
                        ("date_to", "!=", False),
                        ("date_from", "<=", record.date_from),
                    ]
                )

            existing = self.search(domain, limit=1)
            if existing:
                raise ValidationError(
                    _(
                        "There is already an active approval for supplier %(supplier)s "
                        "and product %(product)s in the same date range."
                    )
                    % {
                        "supplier": record.partner_id.name,
                        "product": record.product_tmpl_id.name,
                    }
                )
