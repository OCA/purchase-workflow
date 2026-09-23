# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import datetime

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    approved_supplier_ids = fields.One2many(
        "purchase.supplier.approved",
        "product_tmpl_id",
        string="Approved Suppliers",
        help="List of approved suppliers for this product",
    )
    approved_supplier_count = fields.Integer(
        string="Approved Suppliers Count",
        compute="_compute_approved_supplier_count",
    )
    approved_supplier_requirement = fields.Selection(
        [
            ("", "Use Category Setting"),
            ("required", "Required"),
            ("not_required", "Not Required"),
        ],
        help="Override the category setting for approved supplier requirement. "
        "If not set, the category setting will be used.",
    )
    is_approved_supplier_required = fields.Boolean(
        string="Require Approved Suppliers",
        compute="_compute_is_approved_supplier_required",
        store=True,
        help="Effective requirement for approved suppliers"
        " based on category and exception settings.",
    )

    @api.depends("approved_supplier_ids")
    def _compute_approved_supplier_count(self):
        for record in self:
            record.approved_supplier_count = len(record.approved_supplier_ids)

    def is_supplier_approved(self, partner_id, date=None):
        """Check if a supplier is approved for this product on a specific date"""
        self.ensure_one()
        if not self.is_approved_supplier_required:
            return True

        if not date:
            date = fields.Date.context_today(self)
        elif isinstance(date, datetime.datetime):
            date = date.date()

        approved_supplier = self.approved_supplier_ids.filtered(
            lambda s: s.partner_id.id == partner_id
            and s.active
            and (s.date_from and s.date_from <= date)
            and (not s.date_to or (s.date_to and s.date_to >= date))
        )
        return bool(approved_supplier)

    @api.depends("approved_supplier_requirement", "categ_id.require_approved_supplier")
    def _compute_is_approved_supplier_required(self):
        for record in self:
            category_requirement = (
                record.categ_id.require_approved_supplier if record.categ_id else False
            )
            if record.approved_supplier_requirement == "required":
                record.is_approved_supplier_required = True
            elif record.approved_supplier_requirement == "not_required":
                record.is_approved_supplier_required = False
            else:
                record.is_approved_supplier_required = category_requirement

    def action_view_approved_suppliers(self):
        """Action to view approved suppliers for this product"""
        self.ensure_one()
        action = self.env.ref(
            "purchase_supplier_approved.action_purchase_supplier_approved"
        ).read()[0]
        action["domain"] = [("product_tmpl_id", "=", self.id)]
        action["context"] = {
            "default_product_tmpl_id": self.id,
            "search_default_product_tmpl_id": self.id,
        }
        if self.approved_supplier_count == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = self.approved_supplier_ids[0].id
        return action
