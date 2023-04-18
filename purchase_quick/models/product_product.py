# © 2014 Today Akretion
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from lxml import etree

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    po_line_ids = fields.One2many(
        comodel_name="purchase.order.line",
        inverse_name="product_id",
        help="Technical: used to compute quantities to purchase.",
    )
    seller_price = fields.Float(compute="_compute_seller_price")

    def _compute_seller_price(self):
        po = self.pma_parent
        for record in self:
            seller = record._select_seller(
                partner_id=po.partner_id,
                quantity=record.qty_to_process or 1,
                uom_id=record.quick_uom_id,
            )
            price_unit = record.uom_id._compute_price(
                seller.price,
                record.quick_uom_id,
            )
            if self.pma_parent.currency_id != seller.currency_id:
                price_unit = seller.currency_id._convert(
                    price_unit, po.currency_id, po.company_id, po.date_order.date()
                )
            record.seller_price = price_unit

    def _default_quick_uom_id(self):
        if self.env.context.get("parent_model", False) == "purchase.order":
            return self.uom_po_id
        return super()._default_quick_uom_id()

    def _compute_process_qty_purchase(self):
        po_lines = self.env["purchase.order.line"].search(
            [("order_id", "=", self.env.context.get("parent_id"))]
        )
        for product in self:
            product.qty_to_process = sum(
                po_lines.filtered(lambda l: l.product_id == product).mapped(
                    "product_qty"
                )
            )

    @api.depends("po_line_ids")
    def _compute_process_qty(self):
        res = super(ProductProduct, self)._compute_process_qty()
        if self.env.context.get("parent_model", False) == "purchase.order":
            self._compute_process_qty_purchase()
        return res

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        purchase = self.env["purchase.order"].browse(self.env.context.get("parent_id"))
        if self.env.context.get("in_current_parent") and purchase:
            po_lines = self.env["purchase.order.line"].search(
                [("order_id", "=", purchase.id)]
            )
            args.append(("id", "in", po_lines.mapped("product_id").ids))
        return super(ProductProduct, self).search(
            args, offset=offset, limit=limit, order=order, count=count
        )

    def _get_supplier_domain(self, partner_id):
        return [
            "|",
            ("variant_specific_seller_ids.name", "=", partner_id),
            "&",
            ("seller_ids.name", "=", partner_id),
            ("product_variant_ids", "!=", False),
        ]

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False
        )
        po_partner_id = self.env.context.get("po_partner_id")
        if view_type == "search" and po_partner_id:
            doc = etree.XML(res["arch"])
            node = doc.xpath("//filter[@name='filter_for_current_supplier']")
            if node:
                node[0].attrib["domain"] = str(self._get_supplier_domain(po_partner_id))
                res["arch"] = etree.tostring(doc, pretty_print=True)
        return res

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        """hijack product edition rights if we're in the mass edition menu"""
        if self.env.context.get("quick_access_rights_purchase"):
            return self.env["purchase.order.line"].check_access_rights(
                operation, raise_exception
            )
        return super().check_access_rights(operation, raise_exception)
