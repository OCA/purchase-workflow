# © 2014 Today Akretion
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    # for searching purpose
    variant_specific_seller_ids = fields.One2many(
        "product.supplierinfo", "product_id"
    )
    po_line_ids = fields.One2many(
        comodel_name="purchase.order.line",
        inverse_name="product_id",
        help="Technical: used to compute quantities to purchase.",
    )

    @api.depends("po_line_ids")
    def _compute_process_qty(self):
        res = super(ProductProduct, self)._compute_process_qty()
        if self.env.context.get("parent_model", False) == "purchase.order":
            po_lines = self.env["purchase.order.line"].search(
                [("order_id", "=", self.env.context.get("parent_id"))]
            )
            for product in self:
                product_po_lines = po_lines.filtered(
                    lambda l, p=product: l.product_id == p
                )
                for product_po_line in product_po_lines:
                    product.qty_to_process += product_po_line.product_qty
        return res

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        purchase = self.env["purchase.order"].browse(
            self.env.context.get("parent_id")
        )
        if self.env.context.get("in_current_parent") and purchase:
            po_lines = self.env["purchase.order.line"].search(
                [("order_id", "=", purchase.id)]
            )
            args.append((("id", "in", po_lines.mapped("product_id").ids)))
        if self.env.context.get("for_current_supplier") and purchase:
            seller = purchase.partner_id
            seller = seller.commercial_partner_id or seller
            args += [
                "|",
                ("variant_specific_seller_ids.name", "=", seller.id),
                "&",
                ("seller_ids.name", "=", seller.id),
                ("product_variant_ids", "!=", False),
            ]
        return super(ProductProduct, self).search(
            args, offset=offset, limit=limit, order=order, count=count
        )
