# © 2014 Today Akretion
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    # for searching purpose
    variant_specific_seller_ids = fields.One2many("product.supplierinfo", "product_id")
    po_line_ids = fields.One2many(
        comodel_name="purchase.order.line",
        inverse_name="product_id",
        help="Technical: used to compute quantities to purchase.",
    )
    purchase_quick_uom_category_id = fields.Many2one(related="uom_po_id.category_id")
    purchase_quick_uom_id = fields.Many2one(
        "uom.uom",
        domain="[('category_id', '=', purchase_quick_uom_category_id)]",
        compute="_compute_purchase_quick_uom_id",
        # TODO cleanup base module to make it cleaner ?
        #  Whether we update quantities or uom,
        #  we should be refreshing the line anyways
        #  + it is not possible to call our own functionhere: several _inverse
        #  means only the first one will get the values in the UI
        #  and all the subsequent ones will discard the values
        inverse="_inverse_set_process_qty",
    )

    def _default_purchase_quick_uom_id(self):
        return self.uom_po_id

    def _compute_purchase_quick_uom_id(self):
        parent_model = self.env.context.get("parent_model")
        parent_id = self.env.context.get("parent_id")
        if parent_model and parent_id:
            parent = self.env[parent_model].browse(parent_id)
            for rec in self:
                quick_line = parent._get_quick_line(rec)
                if quick_line:
                    rec.purchase_quick_uom_id = quick_line.product_uom
                else:
                    rec.purchase_quick_uom_id = rec._default_purchase_quick_uom_id()

    @api.depends("po_line_ids")
    def _compute_process_qty(self):
        res = super(ProductProduct, self)._compute_process_qty()
        if self.env.context.get("parent_model", False) == "purchase.order":
            po_lines = self.env["purchase.order.line"].search(
                [("order_id", "=", self.env.context.get("parent_id"))]
            )
            for product in self:
                total_prod_qty = 0.0
                product_po_lines = po_lines.filtered(
                    lambda l, p=product: l.product_id == p
                )
                for product_po_line in product_po_lines:
                    total_prod_qty += product_po_line.product_qty
                product.qty_to_process += total_prod_qty
        return res

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        purchase = self.env["purchase.order"].browse(self.env.context.get("parent_id"))
        if self.env.context.get("in_current_parent") and purchase:
            po_lines = self.env["purchase.order.line"].search(
                [("order_id", "=", purchase.id)]
            )
            args.append(("id", "in", po_lines.mapped("product_id").ids))
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
