# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        # For new PO lines we set the product packaging if present in
        # the procurement values.
        vals = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        if values.get("product_packaging_id"):
            vals["product_packaging_id"] = values.get("product_packaging_id").id
            packaging_id = self.env["product.packaging"].browse(
                vals["product_packaging_id"]
            )
            if vals["product_qty"] % packaging_id.qty != 0:
                qty = ((vals["product_qty"] // packaging_id.qty) + 1) * packaging_id.qty
                vals["product_qty"] = qty
        return vals

    def _find_candidate(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
    ):
        """Recovery of this function to add the notion of packaging in the filtered"""

        description_picking = ""
        if values.get("product_description_variants"):
            description_picking = values["product_description_variants"]
        lines = self.filtered(
            lambda l: l.propagate_cancel == values["propagate_cancel"]
            and (
                l.orderpoint_id == values["orderpoint_id"]
                if values.get("orderpoint_id") and not values.get("move_dest_ids")
                else True
            )
            and l.product_packaging_id == values["product_packaging_id"]
            if values.get("product_packaging_id")
            else True
        )
        # In case 'product_description_variants' is in the values, we also filter on the PO line
        # name. This way, we can merge lines with the same description. To do so, we need the
        # product name in the context of the PO partner.
        if lines and values.get("product_description_variants"):
            partner = self.mapped("order_id.partner_id")[:1]
            product_lang = product_id.with_context(
                lang=partner.lang,
                partner_id=partner.id,
            )
            name = product_lang.display_name
            if product_lang.description_purchase:
                name += "\n" + product_lang.description_purchase
            lines = lines.filtered(
                lambda l: l.name == name + "\n" + description_picking
            )
            if lines:
                return lines[0]

        return lines and lines[0] or self.env["purchase.order.line"]
